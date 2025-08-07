from pathlib import Path
from typing import List, Union
from ase.io import read as ase_read, write as ase_write, Trajectory
from ase.atoms import Atoms

from .formats import read_bcs, write_bcs
from solidkit.core.decorators import extended_func_decorator

__all__ = [
    'read', 'write', 'Trajectory'
]

def _read_ext(filename: str, *args, **kwargs) -> Union[Atoms, List[Atoms]]:
    if Path(filename).suffix.lower() == '.bcs':
        atoms = read_bcs(filename)
    else:
        atoms = ase_read(filename, *args, **kwargs)
    return atoms

def _write_ext(filename, atoms, *args, **kwargs):
    if Path(filename).suffix.lower() == '.bcs':
        write_bcs(filename, atoms, *args, **kwargs)
    else:
        ase_write(filename, atoms, *args, **kwargs)

read = extended_func_decorator(ase_read, _read_ext)
write = extended_func_decorator(ase_write, _write_ext)
