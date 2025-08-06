# Copyright (c) 2010-2025 The Regents of the University of Michigan
# This file is from the freud project, released under the BSD 3-Clause License.


# start delvewheel patch
def _delvewheel_patch_1_11_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'freud_analysis.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-freud_analysis-3.4.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-freud_analysis-3.4.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_0()
del _delvewheel_patch_1_11_0
# end delvewheel patch

# density,
from . import (
    box,
    cluster,
    data,
    density,
    diffraction,
    environment,
    interface,
    locality,
    msd,
    order,
    parallel,
    pmft,
)
from .box import Box
from .locality import AABBQuery, LinkCell, NeighborList
from .parallel import NumThreads, get_num_threads, set_num_threads

# Override TBB's default autoselection. This is necessary because once the
# automatic selection runs, the user cannot change it.
set_num_threads(0)

__version__ = "3.4.0"

__all__ = [
    "AABBQuery",
    "Box",
    "LinkCell",
    "NeighborList",
    "NumThreads",
    "__version__",
    "box",
    "cluster",
    "data",
    "density",
    "diffraction",
    "environment",
    "get_num_threads",
    "interface",
    "locality",
    "msd",
    "order",
    "parallel",
    "pmft",
    "set_num_threads",
]

__citation__ = """@article{freud2020,
    title = {freud: A Software Suite for High Throughput
             Analysis of Particle Simulation Data},
    author = {Vyas Ramasubramani and
              Bradley D. Dice and
              Eric S. Harper and
              Matthew P. Spellings and
              Joshua A. Anderson and
              Sharon C. Glotzer},
    journal = {Computer Physics Communications},
    volume = {254},
    pages = {107275},
    year = {2020},
    issn = {0010-4655},
    doi = {https://doi.org/10.1016/j.cpc.2020.107275},
    url = {http://www.sciencedirect.com/science/article/pii/S0010465520300916},
    keywords = {Simulation analysis, Molecular dynamics, Monte Carlo,
                Computational materials science},
}"""
