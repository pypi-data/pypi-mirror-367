# (C) Copyright 2024- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

"""
Custom Cascade Runner

Used for when providing initial conditions
"""

from __future__ import annotations

import logging
from typing import Any
from typing import Dict
from typing import List

from anemoi.inference.config import Configuration
from anemoi.inference.forcings import BoundaryForcings
from anemoi.inference.forcings import ComputedForcings
from anemoi.inference.forcings import CoupledForcings
from anemoi.inference.forcings import Forcings
from anemoi.inference.input import Input
from anemoi.inference.inputs import create_input
from anemoi.inference.runner import Runner
from anemoi.inference.types import IntArray
from anemoi.utils.config import DotDict

LOG = logging.getLogger(__name__)


class CascadeRunner(Runner):
    """Cascade Inference Runner"""

    def __init__(self, config: dict | Configuration, **kwargs):

        if isinstance(config, dict):
            # So we get the dot notation
            config = DotDict(config)

        self.config = config

        default_init_args = dict(
            checkpoint=config.checkpoint,
            device=config.device,
            precision=config.precision,
            allow_nans=config.allow_nans,
            verbosity=config.verbosity,
            report_error=config.report_error,
            use_grib_paramid=config.use_grib_paramid,
            development_hacks=config.development_hacks,
        )
        default_init_args.update(kwargs)

        super().__init__(**default_init_args)

        # TODO: REMOVE WHEN ANEMOI-INFERENCE HAS BETTER DEVICE HANDLING
        import torch

        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

    def create_input(self) -> Input:
        """Create the input.

        Returns
        -------
        Input
            The created input.
        """
        input = create_input(self, self.config.input)
        LOG.info("Input: %s", input)
        return input

    def create_constant_computed_forcings(self, variables: List[str], mask: IntArray) -> List[Forcings]:
        """Create constant computed forcings.

        Parameters
        ----------
        variables : List[str]
            The variables for the forcings.
        mask : IntArray
            The mask for the forcings.

        Returns
        -------
        List[Forcings]
            The created constant computed forcings.
        """
        result = ComputedForcings(self, variables, mask)
        LOG.info("Constant computed forcing: %s", result)
        return [result]

    def create_dynamic_computed_forcings(self, variables: List[str], mask: IntArray) -> List[Forcings]:
        """Create dynamic computed forcings.

        Parameters
        ----------
        variables : List[str]
            The variables for the forcings.
        mask : IntArray
            The mask for the forcings.

        Returns
        -------
        List[Forcings]
            The created dynamic computed forcings.
        """
        result = ComputedForcings(self, variables, mask)
        LOG.info("Dynamic computed forcing: %s", result)
        return [result]

    def _input_forcings(self, name: str) -> Dict[str, Any]:
        """Get the input forcings configuration.

        Parameters
        ----------
        name : str
            The name of the forcings configuration.

        Returns
        -------
        dict
            The input forcings configuration.
        """
        if self.config.forcings is None:
            # Use the same as the input
            return self.config.input

        if name in self.config.forcings:
            return self.config.forcings[name]

        if "input" in self.config.forcings:
            return self.config.forcings.input

        return self.config.forcings

    def create_constant_coupled_forcings(self, variables: List[str], mask: IntArray) -> List[Forcings]:
        """Create constant coupled forcings.

        Parameters
        ----------
        variables : list
            The variables for the forcings.
        mask : IntArray
            The mask for the forcings.

        Returns
        -------
        List[Forcings]
            The created constant coupled forcings.
        """
        input = create_input(self, self._input_forcings("constant"))
        result = CoupledForcings(self, input, variables, mask)
        LOG.info("Constant coupled forcing: %s", result)
        return [result]

    def create_dynamic_coupled_forcings(self, variables: List[str], mask: IntArray) -> List[Forcings]:
        """Create dynamic coupled forcings.

        Parameters
        ----------
        variables : list
            The variables for the forcings.
        mask : IntArray
            The mask for the forcings.

        Returns
        -------
        List[Forcings]
            The created dynamic coupled forcings.
        """
        input = create_input(self, self._input_forcings("dynamic"))
        result = CoupledForcings(self, input, variables, mask)
        LOG.info("Dynamic coupled forcing: %s", result)
        return [result]

    def create_boundary_forcings(self, variables: List[str], mask: IntArray) -> List[Forcings]:
        """Create boundary forcings.

        Parameters
        ----------
        variables : list
            The variables for the forcings.
        mask : IntArray
            The mask for the forcings.

        Returns
        -------
        List[Forcings]
            The created boundary forcings.
        """
        input = create_input(self, self._input_forcings("boundary"))
        result = BoundaryForcings(self, input, variables, mask)
        LOG.info("Boundary forcing: %s", result)
        return [result]
