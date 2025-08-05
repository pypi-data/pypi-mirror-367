# (C) Copyright 2024- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from __future__ import annotations

import datetime
import functools
from typing import TYPE_CHECKING
from typing import Any
from typing import Generator
from typing import Optional

from anemoi.inference.config.run import RunConfiguration
from anemoi.inference.types import State
from anemoi.utils.dates import frequency_to_seconds
from anemoi.utils.dates import frequency_to_timedelta as to_timedelta
from anemoi.utils.grib import shortname_to_paramid
from earthkit.data import ArrayField
from earthkit.data import FieldList
from earthkit.data import SimpleFieldList

from earthkit.workflows import fluent
from earthkit.workflows import mark
from earthkit.workflows.plugins.anemoi.runner import CascadeRunner
from earthkit.workflows.plugins.anemoi.types import ENSEMBLE_DIMENSION_NAME

if TYPE_CHECKING:
    from anemoi.inference.input import Input
    from anemoi.transform.variables import Variable

    from earthkit.workflows.plugins.anemoi.types import DATE
    from earthkit.workflows.plugins.anemoi.types import ENSEMBLE_MEMBER_SPECIFICATION
    from earthkit.workflows.plugins.anemoi.types import LEAD_TIME


def _parse_date(date: DATE) -> datetime.datetime:
    """Parse date from string or tuple"""
    if isinstance(date, datetime.datetime):
        return date
    elif isinstance(date, str):
        return datetime.datetime.fromisoformat(date)
    else:
        return datetime.datetime(*date)


def _get_initial_conditions(input: Input, date: DATE) -> State:
    """Get initial conditions for the model"""
    input_state = input.create_input_state(date=_parse_date(date))
    assert isinstance(input_state, dict), "Input state must be a dictionary"
    input_state.pop("_grib_templates_for_output", None)

    return input_state


def _get_initial_conditions_from_config(config: dict[str, Any], date: DATE) -> State:
    """Get initial conditions for the model"""
    runner = CascadeRunner(config)
    input = runner.create_input()
    return _get_initial_conditions(input, date)


def _get_initial_conditions_ens(input: Input, ens_mem: int, date: DATE) -> State:
    """Get initial conditions for the model"""
    from anemoi.inference.inputs.mars import MarsInput

    if isinstance(input, MarsInput):  # type: ignore
        input.kwargs["number"] = ens_mem  # type: ignore

    input_state = input.create_input_state(date=_parse_date(date))
    assert isinstance(input_state, dict), "Input state must be a dictionary"
    input_state["ensemble_member"] = ens_mem
    input_state.pop("_grib_templates_for_output", None)

    return input_state


def _get_initial_conditions_ens_from_config(
    config: dict[str, Any],
    ens_mem: int,
    date: DATE,
) -> State:
    """Get initial conditions for the model"""
    runner = CascadeRunner(config)
    input = runner.create_input()
    return _get_initial_conditions_ens(input, date, ens_mem)


def _transform_fake(act: fluent.Action, ens_num: int) -> fluent.Action:
    """Transform the action to simulate ensemble members"""

    def _empty_payload(x, ens_mem: int):
        assert isinstance(x, dict), "Input state must be a dictionary"
        x["ensemble_member"] = ens_mem
        return x

    return act.map(fluent.Payload(_empty_payload, [fluent.Node.input_name(0), ens_num]))


def _parse_ensemble_members(ensemble_members: ENSEMBLE_MEMBER_SPECIFICATION) -> list[int]:
    """Parse ensemble members"""
    if isinstance(ensemble_members, int):
        if ensemble_members < 1:
            raise ValueError("Number of ensemble members must be greater than 0.")
        return list(range(ensemble_members))
    return list(ensemble_members)


def get_initial_conditions_source(
    config: RunConfiguration | fluent.Action,
    date: DATE,
    ensemble_members: ENSEMBLE_MEMBER_SPECIFICATION = 1,
    *,
    initial_condition_perturbation: bool = False,
    payload_metadata: Optional[dict[str, Any]] = None,
) -> fluent.Action:
    """
    Get the initial conditions for the model

    Parameters
    ----------
    config : RunConfiguration | fluent.Action
        Configuration object, must contain checkpoint and input.
        If is a fluent action, the action must return the RunConfiguration object.
    date : str | tuple[int, int, int]
        Date to get initial conditions for
    ensemble_members : ENSEMBLE_MEMBER_SPECIFICATION, optional
        Number of ensemble members to get, by default 1
    initial_condition_perturbation : bool, optional
        Whether to get perturbed initial conditions, by default False
        If False, only one initial condition is returned, and
        the ensemble members are simulated by wrapping the action.
    payload_metadata : Optional[dict[str, Any]], optional
        Metadata to add to the payload, by default None

    Returns
    -------
    fluent.Action
        Fluent action of the initial conditions
    """
    ensemble_members = _parse_ensemble_members(ensemble_members)
    if initial_condition_perturbation:
        if isinstance(config, fluent.Action):
            init_conditions = config.transform(
                lambda x, *a: x.map(
                    fluent.Payload(
                        _get_initial_conditions_ens_from_config,
                        args=(fluent.Node.input_name(0), *a),
                        kwargs=dict(date=date),
                        metadata=payload_metadata,
                    )
                ),
                params=ensemble_members,
                dim=(ENSEMBLE_DIMENSION_NAME, ensemble_members),
            )
            init_conditions._add_dimension("date", [_parse_date(date)])
            return init_conditions

        return fluent.from_source(
            [
                [
                    # fluent.Payload(_get_initial_conditions_ens, kwargs=dict(input=input, date=date, ens_mem=ens_mem))
                    fluent.Payload(
                        _get_initial_conditions_ens_from_config,
                        kwargs=dict(config=config, date=date, ens_mem=ens_mem),
                        metadata=payload_metadata,
                    )
                    for ens_mem in ensemble_members
                ],
            ],  # type: ignore
            coords={"date": [_parse_date(date)], ENSEMBLE_DIMENSION_NAME: ensemble_members},
        )

    if isinstance(config, fluent.Action):
        init_condition = fluent.Payload(
            _get_initial_conditions_from_config,
            args=(fluent.Node.input_name(0),),
            kwargs=dict(date=date),
            metadata=payload_metadata,
        )
        single_init = config.map(init_condition)
        single_init._add_dimension("date", [_parse_date(date)])
    else:
        init_condition = fluent.Payload(
            _get_initial_conditions_from_config, kwargs=dict(config=config, date=date), metadata=payload_metadata
        )
        single_init = fluent.from_source(
            [
                init_condition,
            ],  # type: ignore
            coords={"date": [_parse_date(date)]},
        )

    # Wrap with empty payload to simulate ensemble members
    expanded_init = single_init.transform(
        _transform_fake,
        list(zip(ensemble_members)),
        (ENSEMBLE_DIMENSION_NAME, ensemble_members),  # type: ignore
    )
    if ENSEMBLE_DIMENSION_NAME not in expanded_init.nodes.coords:
        expanded_init.nodes = expanded_init.nodes.expand_dims(ENSEMBLE_DIMENSION_NAME)
    return expanded_init


def _time_range(
    start: datetime.datetime, end: datetime.datetime, step: datetime.timedelta
) -> Generator[datetime.datetime, None, None]:
    """Get a range of timedeltas"""
    while start < end:
        yield start
        start += step


def _expand(runner: CascadeRunner, model_results: fluent.Action) -> fluent.Action:
    """Expand model results into the parameter dimension"""

    # Expand by variable
    variables = [*runner.checkpoint.diagnostic_variables, *runner.checkpoint.prognostic_variables]

    # Seperate surface and pressure variables
    surface_vars = [var for var in variables if "_" not in var]

    pressure_vars_complete = [var for var in variables if "_" in var]
    # pressure_vars = list(set(var.split("_")[0] for var in variables if "_" in var))
    # pressure_levels = list(set(var.split('_')[1] for var in variables if "_" in var))

    surface_expansion = None
    if surface_vars:
        surface_expansion = model_results.expand(
            ("param", surface_vars), ("param", surface_vars), backend_kwargs=dict(method="sel")
        )

    pressure_expansion = None
    if pressure_vars_complete:
        pressure_expansion = model_results.expand(
            ("param", pressure_vars_complete),
            ("param", pressure_vars_complete),
            backend_kwargs=dict(method="sel", remapping={"param": "{param}_{level}"}),
        )
        # pressure_expansion = model_results.expand(
        #     ("param", pressure_vars), ("param", pressure_vars), backend_kwargs=dict(method="sel")
        # )
        # pressure_expansion = pressure_expansion.expand(('level', pressure_levels), ('level', pressure_levels), backend_kwargs=dict(method="sel"))

    if surface_expansion is not None and pressure_expansion is not None:
        model_results = surface_expansion.join(pressure_expansion, dim="param")
    elif surface_expansion is not None:
        model_results = surface_expansion
    elif pressure_expansion is not None:
        model_results = pressure_expansion
    else:
        raise ValueError("No variables to expand")

    return model_results


def run_model(
    runner: CascadeRunner,
    config: RunConfiguration,
    input_state_source: fluent.Action,
    lead_time: LEAD_TIME,
    payload_metadata: Optional[dict[str, Any]] = None,
    **kwargs,
) -> fluent.Action:
    """
    Run the model, expanding the results to the correct dimensions.

    Parameters
    ----------
    runner : Runner
        `anemoi.inference` runner
    config : RunConfiguration
        Configuration object
    input_state_source : fluent.Action
        Fluent action of initial conditions
    lead_time : LEAD_TIME
        Lead time to run out to. Can be a string,
        i.e. `1H`, `1D`, int, or a datetime.timedelta
    payload_metadata : Optional[dict[str, Any]], optional
        Metadata to add to the payload, by default None
    kwargs : dict
        Additional arguments to pass to the runner

    Returns
    -------
    fluent.Action
        Cascade action of the model results
    """
    lead_time = to_timedelta(lead_time)

    model_payload = fluent.Payload(
        run_as_earthkit_from_config,
        args=(fluent.Node.input_name(0),),
        kwargs=dict(config=config, lead_time=lead_time, **kwargs),
        metadata=payload_metadata,
    )

    model_step = runner.checkpoint.timestep
    steps = list(
        map(lambda x: frequency_to_seconds(x) // 3600, _time_range(model_step, lead_time + model_step, model_step))
    )

    model_results = input_state_source.map(model_payload, yields=("step", steps))

    return _expand(runner, model_results)


def _paramId_to_units(paramId: int) -> str:
    """Get the units for a given paramId."""
    from eccodes import codes_get
    from eccodes import codes_grib_new_from_samples
    from eccodes import codes_release
    from eccodes import codes_set

    gid = codes_grib_new_from_samples("GRIB2")

    codes_set(gid, "paramId", paramId)
    units = codes_get(gid, "units")
    codes_release(gid)
    return units


@mark.needs_gpu
def run_as_earthkit(
    input_state: dict, runner: CascadeRunner, lead_time: LEAD_TIME, extra_metadata: dict[str, Any] = None
) -> Generator[SimpleFieldList, None, None]:
    """
    Run the model and yield the results as earthkit FieldList

    Parameters
    ----------
    input_state : dict
        Initial Conditions for the model
    runner : CascadeRunner
        CascadeRunner Object
    lead_time : LEAD_TIME
        Lead time for the model
    extra_metadata: dict[str, Any], optional
        Extra metadata to add to the fields, by default None

    Returns
    -------
    Generator[SimpleFieldList, None, None]
        State of the model at each time step
    """
    import os

    if hasattr(runner.config, "env"):
        # Set environment variables found in the configuration
        for key, value in runner.config.env.items():
            os.environ[key] = str(value)

    initial_date: datetime.datetime = input_state["date"]
    ensemble_member = input_state.get("ensemble_member")
    extra_metadata = extra_metadata or {}

    variables: dict[str, Variable] = runner.checkpoint.typed_variables

    for state in runner.run(input_state=input_state, lead_time=lead_time):
        fields = []
        step = frequency_to_seconds(state["date"] - initial_date) // 3600

        for field in state["fields"]:
            array = state["fields"][field]
            if "_grib_templates_for_output" in state and field in state["_grib_templates_for_output"]:
                metadata = state["_grib_templates_for_output"][field].metadata()
                metadata = metadata.override(
                    {"step": step, "ensemble_member": ensemble_member, **extra_metadata}, headers_only_clone=False
                )  # 'date': time_to_grib(initial_date), 'time': time_to_grib(initial_date)

            else:
                var = variables[field]

                metadata = {}
                paramId = shortname_to_paramid(var.grib_keys["param"])

                metadata.update(
                    {
                        "step": step,
                        "base_datetime": initial_date,
                        "valid_datetime": state["date"],
                        "shortName": var.name,
                        "short_name": var.name,
                        "paramId": paramId,
                        "levtype": var.grib_keys.get("levtype", None),
                        "latitudes": runner.checkpoint.latitudes,
                        "longitudes": runner.checkpoint.longitudes,
                        "member": ensemble_member,
                        "units": _paramId_to_units(paramId),
                        "edition": 2,
                    }
                )
                metadata.update(extra_metadata)

            fields.append(ArrayField(array, metadata))

        yield FieldList.from_fields(fields)
    del runner.model


@functools.wraps(run_as_earthkit)
@mark.needs_gpu
def run_as_earthkit_from_config(
    input_state: dict, config: RunConfiguration, lead_time: LEAD_TIME, extra_metadata: dict[str, Any] = None
) -> Generator[SimpleFieldList, None, None]:
    """Run from config"""
    runner = CascadeRunner(config)
    yield from run_as_earthkit(input_state, runner, lead_time, extra_metadata)


@mark.needs_gpu
def collect_as_earthkit(
    input_state: dict, runner: CascadeRunner, lead_time: LEAD_TIME, extra_metadata: dict[str, Any] = None
) -> SimpleFieldList:
    """
    Collect the results of the model run as earthkit FieldList

    Parameters
    ----------
    input_state : dict
        Initial conditions for the model
    runner : CascadeRunner
        CascadeRunner object
    lead_time : LEAD_TIME
        Lead time for the model
    extra_metadata: dict[str, Any], optional
        Extra metadata to add to the fields, by default None

    Returns
    -------
    SimpleFieldList
        Combined FieldList of the model run
    """
    fields = []
    for state in run_as_earthkit(input_state, runner, lead_time, extra_metadata):
        fields.extend(state.fields)

    return SimpleFieldList(fields)


@functools.wraps(collect_as_earthkit)
@mark.needs_gpu
def collect_as_earthkit_from_config(
    input_state: dict, config: RunConfiguration, lead_time: Any, extra_metadata: dict[str, Any] = None
) -> SimpleFieldList:
    """Run from config"""
    runner = CascadeRunner(config)
    return collect_as_earthkit(input_state, runner, lead_time, extra_metadata)
