#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ase.filters import ExpCellFilter
from ase.optimize import LBFGS, MDMin, FIRE, BFGS, FIRE2, LBFGSLineSearch

def optimize_structure(atoms, fmax=0.005, optimizer_name='LBFGS', calculator=None, stress_sign=True):
    """
    Performs geometry and cell optimization for a given atomic structure.

    This function attaches an ASE calculator, applies a potential-specific stress
    correction if needed, and runs a user-selected optimization algorithm to
    relax the atomic positions and the unit cell.

    Note: The stress modification (stress_sign=False: `stress *= -1.0`) is needed for different definition of stress.
          Like Tersoff calculator of ASE==3.25.0.
    Args:
        atoms (ase.Atoms): The ASE Atoms object to be optimized.
        calculator (ase.calculators.calculator.Calculator): The ASE calculator
            to use for energy and force calculations.
        fmax (float): The maximum tolerance for the optimization convergence,
        optimizer_name (str): The name of the ASE optimizer to use.
            Supported options: 'LBFGS', 'FIRE' and 'MDMin'. Defaults to 'LBFGS'.

    Returns:
        ase.Atoms: The optimized ASE Atoms object.
    """
    # This wrapper function modifies the stress reported by the calculator.
    def calculate_modify_stress(self, *args, **kwargs):
        self.calculate_old(self, *args, **kwargs)
        if 'stress' in self.results:
            self.results['stress'] *= -1.0

    if not calculator: calculator = atoms.calc
    if not stress_sign:
        if not hasattr(calculator, 'calculate_old'):
            calculator.calculate_old = calculator.calculate
            calculator.calculate = calculate_modify_stress.__get__(calculator)
    atoms.calc = calculator

    # Use ExpCellFilter to relax atomic positions and cell simultaneously.
    ecf = ExpCellFilter(atoms)

    # A dictionary mapping names to ASE optimizer classes
    optimizer_map = {
        'lbfgs': LBFGS,
        'fire': FIRE,
        'fire2': FIRE2,
        'mdmin': MDMin,
        'bfgs': BFGS,
        'lbfgslinesearch':LBFGSLineSearch,
    }

    optimizer_class = optimizer_map.get(optimizer_name.lower(), None)
    if not optimizer_class:
        raise ValueError(
            f"Unknown optimizer: {optimizer_name}. "
            f"Available options are: {list(optimizer_map.keys())}"
        )

    optimizer = optimizer_class(ecf)
    optimizer.run(fmax=fmax)
    return atoms
