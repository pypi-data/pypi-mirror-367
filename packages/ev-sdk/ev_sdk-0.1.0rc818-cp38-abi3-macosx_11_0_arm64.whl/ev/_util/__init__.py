"""!! PRIVATE MODULE !!

This module provides internal utility functions for importing and managing
jobs and their associated modules. These utilities support dynamic loading
of job definitions from Python files.

Main Functions:
    _import_job: Import a job object from a file reference
    _import_module: Import a Python module from a file path
    _import_obj: Extract specific objects from imported modules
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from ev.job import Job

if TYPE_CHECKING:
    from types import ModuleType

_T = TypeVar("_T")

__all__: list[str] = []


def _import_job(job_reference: str) -> Job:
    """Imports and returns the job object from its reference."""
    try:
        job_ref = _ObjectRef.parse(job_reference)
        job_mod = _import_module(job_ref)
        job: Job = _import_obj(job_mod, Job, job_ref.symbol)
        return job
    except ValueError as e:
        raise ValueError(f"An error occurred while loading the job: '{job_reference}'") from e


@dataclass
class _ObjectRef:
    """Reference to a python object in some file or module."""

    module: str  # TODO(rchowell): support both file and module imports
    symbol: str | None = None

    @staticmethod
    def parse(ref: str) -> _ObjectRef:
        """Parses an object reference from argument from the form `file.py:object`."""
        if ":" in ref:
            file, symbol = ref.split(":", 1)
        else:
            file, symbol = ref, None
        return _ObjectRef(file, symbol)


def _import_module(ref: _ObjectRef) -> ModuleType:
    """Imports the module from a python file, we don't support actual modules yet.

    See: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    """
    if not ref.module.endswith(".py"):
        # TODO(rchowell): support both file and module imports
        raise ValueError(
            f"Invalid object reference, expected a file path (ending in .py) but was given a module name: {ref.module}."
        )

    # this is just the absolute path to the python file for now.
    mod_path = Path(ref.module).resolve()

    # put this python file's dir on the path so imports work just like `python file.py`.
    sys.path.insert(0, str(mod_path.parent))

    # parse the module's name from the file path, needed to create the mod_spec.
    mod_name = inspect.getmodulename(ref.module)
    if mod_name is None:
        raise ValueError(f"Could not determine module name from {ref.module}")

    # the mod_spec is required to actually import this object's module
    mod_spec = importlib.util.spec_from_file_location(mod_name, ref.module)
    if mod_spec is None:
        raise ValueError(f"Could not determine module spec from {mod_name}")

    # add the module symbol (mod_name) to the sys.modules so it's resolvable
    module = importlib.util.module_from_spec(mod_spec)
    sys.modules[mod_name] = module

    # now execute the module code a'la normal import behavior
    try:
        mod_spec.loader.exec_module(module)  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Failed to import module for: {ref}.") from e

    return module


def _import_obj(module: ModuleType, class_: type[_T], symbol: str | None = None) -> _T:
    """Returns an object instance by locating it in the given module."""
    if symbol is not None:
        if not hasattr(module, symbol):
            raise ValueError(f"No {class_} variable `{symbol}` in the given module.")
        elif not isinstance(obj := getattr(module, symbol), class_):
            raise ValueError(
                f"Variable `{symbol}` exists in the given module, but does not have type '{class_}', found {type(obj)}"
            )
        else:
            return obj
    else:
        objs = {name: obj for name, obj in vars(module).items() if isinstance(obj, class_)}
        if len(objs) == 0:
            raise ValueError(f"No {class_}'s were found in this module!")
        elif len(objs) > 1:
            raise ValueError(f"Found multiple {class_}'s in the module: {', '.join(objs.keys())}")
        else:
            return next(iter(objs.values()))
