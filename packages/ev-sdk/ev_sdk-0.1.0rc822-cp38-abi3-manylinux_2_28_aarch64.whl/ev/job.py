from __future__ import annotations

import ast
import inspect
import textwrap
from functools import wraps
from inspect import Parameter
from typing import Callable, ParamSpec, TypeVar, get_args, get_origin

from ev.client import Client
from ev.env import Env
from ev.ev import (
    _Annotation,
    _Arg,
    _Client,
    _Function,
    _Job,
    _JobHandle,
    _Param,
    _Value,
)

_P = ParamSpec("_P")
_R = TypeVar("_R")

# Supported scalar types and their corresponding annotations
_SCALAR_ANNOTATIONS = {
    str: _Annotation.Str,
    bool: _Annotation.Bool,
    int: _Annotation.Int,
    float: _Annotation.Float,
    object: _Annotation.Str,  # TODO(rchowell): support for object-annotated arguments
}

# Supported collection types for validation
_COLLECTION_ANNOTATIONS = {list, dict}


class Job:
    """Job represents an ev program that can be run on the Eventual Platform.

    Args:
        name (str): The name for this job. Defaults to "job".
        env (Env): The environment configuration for this job. Defaults to empty Env().

    Attributes:
        name (str): The name for this job.

    Example:
        >>> job = Job("data-pipeline")
        >>> job = Job("ml-training", env=custom_env)
    """

    _job: _Job

    def __init__(self, name: str = "job", env: Env = Env()) -> None:
        self._job = _Job.new(name, env._env)

    @property
    def name(self) -> str:
        """Get the name identifier of this job.

        Returns:
            str: The name of the job as specified during construction,
                 or "job" if no name was provided.

        Example:
            >>> job = Job("my-data-pipeline")
            >>> print(job.name)
            my-data-pipeline
        """
        return self._job.name

    def main(self) -> Callable[[Callable[_P, _R]], Callable[[], None]]:
        # no doc comment on the decorator.

        # TODO(rchowell): Capture the job.main() decorator arguments.
        # ... no arguments yet.

        # Creates a regular no-arg decorator.
        def decorator(
            function: Callable[_P, _R],
        ) -> Callable[[], None]:
            # This decorator actually sets the function upon *invocation* i.e. job.main() WITH parens.
            if self._job.main:
                raise ValueError("This job's main has already been set!")

            # Create the internal representation of a function which is set on the rust _job
            self._job.main = _new_function(function)

            # The decorated function should not be directly callable!
            @wraps(function)
            def no_call() -> None:
                raise RuntimeError("The job's main is not directly callable.")

            return no_call

        return decorator

    def run(self, client: Client | None = None, args: dict[str, object] | None = None) -> JobHandle:
        """Runs the job on the eventual platform, returning a job handle.

        Args:
            client (Client | None): The client to use for running the job. Defaults to None (uses default client).
            args (dict[str, object] | None): Arguments to pass to the job. Defaults to None.

        Returns:
            JobHandle: A handle to the running job.
        """
        client_to_use: _Client = client._client if client else Client.default()._client
        main_args = [_Arg(k, _Value(v)) for (k, v) in args.items()] if args else []
        handle = client_to_use.run(self._job, main_args)
        return JobHandle(handle)


# TODO(rchowell): move to internalized package
def _new_function(function: Callable[_P, _R]) -> _Function:
    # Builds the internal representation of a function.
    module = inspect.getmodule(function)

    # We need the file so we can include it for packaging.
    # TODO(rchowell): support module style imports
    if not hasattr(module, "__file__"):
        raise ValueError("An ev function must be declared in a file-based module.")

    # Assert the function is NOT defined in a local scope.
    if "<locals>" in function.__qualname__.split("."):
        raise ValueError("An ev function must be declared at a module's top level.")

    # We only need the function's name and its source code, then we can generate the modules.
    py_name = function.__qualname__
    py_code = _get_function_code(function)
    py_params = _get_function_params(function)

    return _Function.from_code(
        py_name,
        py_code,
        py_params,
    )


# TODO(rchowell): move to internalized package
def _get_function_code(function: Callable[_P, _R]) -> str:
    src = inspect.getsource(function)
    src = textwrap.dedent(src)
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function.__name__:
            node.decorator_list = []  # strip the decorator
            return ast.unparse(node)
    raise ValueError(f"Function {function.__name__} was not found in the AST.")


# TODO(rchowell): move to internalized package
def _get_function_params(function: Callable[_P, _R]) -> list[_Param]:
    return [_new_parameter(param) for param in inspect.signature(function).parameters.values()]


# TODO(rchowell): move to internalized package
def _new_parameter(param: Parameter) -> _Param:
    if param.kind == inspect.Parameter.VAR_POSITIONAL:
        raise ValueError(f"Variadic parameters are not supported, found: *{param.name}")
    elif param.kind == inspect.Parameter.VAR_KEYWORD:
        raise ValueError(f"Kwarg parameters are not supported: **{param.name}")
    elif param.annotation is None or param.annotation == inspect._empty:
        raise ValueError(f"Parameter type annotations are required, but found no annotation for {param.name}.")

    hint = param.annotation
    origin = get_origin(hint)
    args = get_args(hint)

    if origin is None and hint in _SCALAR_ANNOTATIONS:
        return _Param(param.name, _SCALAR_ANNOTATIONS[hint])

    if origin is None and hint in _COLLECTION_ANNOTATIONS:
        if hint is list:
            return _Param(param.name, _Annotation.List)
        elif hint is dict:
            return _Param(param.name, _Annotation.Dict)

    if origin in _COLLECTION_ANNOTATIONS:
        if origin is list:
            return _validate_list_annotation(param.name, args)
        elif origin is dict:
            return _validate_dict_annotation(param.name, args)

    raise ValueError(
        f"Unsupported annotation type for parameter '{param.name}': {hint!r}. "
        f"Supported types are: {list(_SCALAR_ANNOTATIONS.keys())}, "
        f"untyped collections: {list(_COLLECTION_ANNOTATIONS)}, "
        f"and typed collections with supported subtypes."
    )


# TODO(rchowell): move to internalized package
def _validate_list_annotation(param_name: str, args: tuple[type]) -> _Param:
    if len(args) != 1:
        raise ValueError(
            f"List annotation for parameter '{param_name}' must have exactly one type argument, "
            f"found {len(args)}: {args}"
        )

    element_type = args[0]

    if element_type not in _SCALAR_ANNOTATIONS:
        raise ValueError(
            f"Unsupported list element type for parameter '{param_name}': {element_type!r}. "
            f"Supported element types are: {list(_SCALAR_ANNOTATIONS.keys())}"
        )

    return _Param(param_name, _Annotation.List)


# TODO(rchowell): move to internalized package
def _validate_dict_annotation(param_name: str, args: tuple[type, type]) -> _Param:
    if len(args) != 2:
        raise ValueError(
            f"Dict annotation for parameter '{param_name}' must have exactly two type arguments (key, value), "
            f"found {len(args)}: {args}"
        )

    key_type, value_type = args

    if key_type not in {str}:  # noqa: FURB171
        raise ValueError(
            f"Unsupported dict key type for parameter '{param_name}': {key_type!r}. "
            f"Only string keys are supported, found: {key_type!r}"
        )

    if value_type not in _SCALAR_ANNOTATIONS:
        raise ValueError(
            f"Unsupported dict value type for parameter '{param_name}': {value_type!r}. "
            f"Supported value types are: {list(_SCALAR_ANNOTATIONS.keys())}"
        )

    return _Param(param_name, _Annotation.Dict)


class JobHandle:
    """JobHandle holds information about a running job.

    Attributes:
        job_id (str): The job identifier.
        job_url (str): The job URL on the Eventual Platform dashboard.
        space_id (str): The space where this job was submitted to.

    Note:
        This constructor is typically not called directly by users.
        JobHandle instances are usually returned by job submission methods.
    """

    _handle: _JobHandle

    def __init__(self, _handle: _JobHandle) -> None:
        self._handle = _handle

    @property
    def job_id(self) -> str:
        """Returns the job id."""
        return self._handle.job_id

    @property
    def job_url(self) -> str:
        """Returns the job url on the Eventual Platform dashboard."""
        return self._handle.job_url

    @property
    def space_id(self) -> str:
        """Returns the space where this job was submitted to."""
        return self._handle.space_id
