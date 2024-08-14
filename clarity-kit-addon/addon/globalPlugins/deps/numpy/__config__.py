# This file is generated by numpy's build process
# It contains system_info results at the time of building this package.
from enum import Enum
from numpy._core._multiarray_umath import (
    __cpu_features__,
    __cpu_baseline__,
    __cpu_dispatch__,
)

__all__ = ["show"]
_built_with_meson = True


class DisplayModes(Enum):
    stdout = "stdout"
    dicts = "dicts"


def _cleanup(d):
    """
    Removes empty values in a `dict` recursively
    This ensures we remove values that Meson could not provide to CONFIG
    """
    if isinstance(d, dict):
        return {k: _cleanup(v) for k, v in d.items() if v and _cleanup(v)}
    else:
        return d


CONFIG = _cleanup(
    {
        "Compilers": {
            "c": {
                "name": "msvc",
                "linker": r"link",
                "version": "19.29.30154",
                "commands": r"cl",
                "args": r"",
                "linker args": r"",
            },
            "cython": {
                "name": "cython",
                "linker": r"cython",
                "version": "3.0.10",
                "commands": r"cython",
                "args": r"",
                "linker args": r"",
            },
            "c++": {
                "name": "msvc",
                "linker": r"link",
                "version": "19.29.30154",
                "commands": r"cl",
                "args": r"",
                "linker args": r"",
            },
        },
        "Machine Information": {
            "host": {
                "cpu": "x86",
                "family": "x86",
                "endian": "little",
                "system": "windows",
            },
            "build": {
                "cpu": "x86",
                "family": "x86",
                "endian": "little",
                "system": "windows",
            },
            "cross-compiled": bool("False".lower().replace("false", "")),
        },
        "Build Dependencies": {
            "blas": {
                "name": "auto",
                "found": bool("False".lower().replace("false", "")),
                "version": "",
                "detection method": "",
                "include directory": r"",
                "lib directory": r"",
                "openblas configuration": r"",
                "pc file directory": r"",
            },
            "lapack": {
                "name": "lapack",
                "found": bool("False".lower().replace("false", "")),
                "version": "",
                "detection method": "",
                "include directory": r"",
                "lib directory": r"",
                "openblas configuration": r"",
                "pc file directory": r"",
            },
        },
        "Python Information": {
            "path": r"C:\Users\runneradmin\AppData\Local\Temp\build-env-4o_lbcon\Scripts\python.exe",
            "version": "3.11",
        },
        "SIMD Extensions": {
            "baseline": __cpu_baseline__,
            "found": [
                feature for feature in __cpu_dispatch__ if __cpu_features__[feature]
            ],
            "not found": [
                feature for feature in __cpu_dispatch__ if not __cpu_features__[feature]
            ],
        },
    }
)


def _check_pyyaml():
    import yaml

    return yaml


def show(mode=DisplayModes.stdout.value):
    """
    Show libraries and system information on which NumPy was built
    and is being used

    Parameters
    ----------
    mode : {`'stdout'`, `'dicts'`}, optional.
        Indicates how to display the config information.
        `'stdout'` prints to console, `'dicts'` returns a dictionary
        of the configuration.

    Returns
    -------
    out : {`dict`, `None`}
        If mode is `'dicts'`, a dict is returned, else None

    See Also
    --------
    get_include : Returns the directory containing NumPy C
                  header files.

    Notes
    -----
    1. The `'stdout'` mode will give more readable
       output if ``pyyaml`` is installed

    """
    if mode == DisplayModes.stdout.value:
        try:  # Non-standard library, check import
            yaml = _check_pyyaml()

            print(yaml.dump(CONFIG))
        except ModuleNotFoundError:
            import warnings
            import json

            warnings.warn("Install `pyyaml` for better output", stacklevel=1)
            print(json.dumps(CONFIG, indent=2))
    elif mode == DisplayModes.dicts.value:
        return CONFIG
    else:
        raise AttributeError(
            f"Invalid `mode`, use one of: {', '.join([e.value for e in DisplayModes])}"
        )