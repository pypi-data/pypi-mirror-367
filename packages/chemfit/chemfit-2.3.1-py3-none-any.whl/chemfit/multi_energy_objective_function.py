from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Callable

from ase import Atoms

from chemfit.ase_objective_function import (
    AtomsFactory,
    AtomsPostProcessor,
    CalculatorFactory,
    EnergyObjectiveFunction,
    ParameterApplier,
)
from chemfit.combined_objective_function import CombinedObjectiveFunction

logger = logging.getLogger(__name__)


def construct_multi_energy_objective_function(
    calc_factory: CalculatorFactory,
    param_applier: ParameterApplier,
    tag_list: Sequence[str],
    reference_energy_list: Sequence[float],
    path_or_factory_list: Sequence[Path | AtomsFactory],
    weight_cb: (
        None | Sequence[Callable[[Atoms], float] | None] | Callable[[Atoms], float]
    ) = None,
    weight_list: Sequence[float] | None = None,
    atom_post_processor_list: Sequence[AtomsPostProcessor | None] | None = None,
) -> CombinedObjectiveFunction:
    """
    Initialize a CombinedObjectiveFunction by constructing individual EnergyObjectiveFunctions.

    Each element of `tag_list`, `path_to_reference_configuration_list`, and `reference_energy_list`
    defines one EnergyObjectiveFunction instance. Those instances are collected and passed to the
    CombinedObjectiveFunction with the provided weights.

    Args:
        tag_list (list[str]):
            A list of labels (tags) for each reference configuration (e.g., "cluster1", "bulk").
        reference_energy_list (list[float]):
            A list of target energies corresponding to each reference configuration.
        path_or_factory_list (list[Union[Path, AtomsFactory]]):
            A list of filesystem paths or atom factories.
        weight_cb (Union[None, list[Callable[[Atoms, float]]], Callable[[Atoms], float], default None):
            Either a single callable or a list of callables for the weight callback or None
        weight_list (Optional[list[float]], optional):
            A list of non-negative floats specifying the combination weight for each
            EnergyObjectiveFunction. If None, all weights default to 1.0.

    Raises:
        AssertionError: If lengths of `tag_list`, `path_to_reference_configuration_list`, and
            `reference_energy_list` differ, or if any provided weight is negative.

    """
    ob_funcs: list[EnergyObjectiveFunction] = []

    n_terms = len(path_or_factory_list)

    if atom_post_processor_list is None:
        atom_post_processor_list = [None] * n_terms

    if weight_cb is None:
        weight_cb_list = [None] * n_terms
    elif not isinstance(weight_cb, Sequence):
        weight_cb_list = [weight_cb] * n_terms
    else:
        assert n_terms == len(weight_cb)
        weight_cb_list = weight_cb

    if weight_list is None:
        weight_list = [1.0 for _ in reference_energy_list]

    for t, p_ref, e_ref, post_proc, weight, w_cb in zip(
        tag_list,
        path_or_factory_list,
        reference_energy_list,
        atom_post_processor_list,
        weight_list,
        weight_cb_list,
    ):
        # First try to find out if p_ref is just a path,
        # or the more general AtomsFactory
        # depending on which it is, we call the constructor differently
        if isinstance(p_ref, Path):
            ob = EnergyObjectiveFunction(
                calc_factory=calc_factory,
                param_applier=param_applier,
                path_to_reference_configuration=p_ref,
                reference_energy=e_ref,
                tag=t,
                atoms_post_processor=post_proc,
                weight=weight,
                weight_cb=w_cb,
            )
        else:
            ob = EnergyObjectiveFunction(
                calc_factory=calc_factory,
                param_applier=param_applier,
                atoms_factory=p_ref,
                reference_energy=e_ref,
                tag=t,
                atoms_post_processor=post_proc,
                weight=weight,
                weight_cb=w_cb,
            )

        ob_funcs.append(ob)

    return CombinedObjectiveFunction(ob_funcs)
