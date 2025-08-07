from __future__ import annotations

import functools
import inspect
import platform
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import MutableMapping, MutableSequence, Sequence

import pathlib

from ev.ev import Secret, _Env


class Env:
    """Env represents a job's runtime environment e.g. local files and python dependencies.

    This class provides functionality to manage Python environments with specific
    versions, dependencies, local file inclusions, and secrets.

    Args:
        python_version(str | None): The Python version to use for this environment.
            If None, uses the current platform's Python version.

    Attributes:
        environ(MutableMapping[str, str]): A mutable mapping of environment variables which are available in the job.
        secrets(MutableSequence[Secret]): A list of Secret objects associated with this environment.

    Examples:
        >>> from ev import Env, Secret
        >>> env = Env("3.11")
        >>> env.pip_install("requirements.txt")
        >>> env.include("/path/to/local.py")
        >>> env.environ["foo"] = "bar"
        >>> env.secrets.append(Secret.from_pydict({"API_KEY": "123"}))
    """

    _env: _Env

    def __init__(self, python_version: str | None = None) -> None:
        self._env = _Env.new(python_version or platform.python_version())

    @property
    def environ(self) -> MutableMapping[str, str]:
        """Returns the environment variable dictionary-like object for this environment.

        Returns:
            MutableMapping[str, str]: A mutable mapping containing environment variables for this environment.

        Examples:
            >>> from ev import Env
            >>> env = Env("3.11")
            >>> env.environ["foo"] = "bar"
        """
        return self._env.environ

    @environ.setter
    def environ(self, environ: dict[str, str]) -> None:
        """Sets the environment variables for this environment from the given dictionary.

        Args:
            environ(dict[str, str]): A dictionary containing environment variables to set.

        Returns:
            None: This method does not return anything.

        Examples:
            >>> from ev import Env
            >>> env = Env("3.11")
            >>> env.environ = {"VAR_1": "abc", "VAR_2": "xyz"}
        """
        self._env.environ = environ

    @property
    def secrets(self) -> MutableSequence[Secret]:
        """Get the Secrets list-like object for this environment.

        Returns:
            MutableSequence[Secret]: The Secrets list-like object.

        Examples:
            >>> from ev import Env
            >>> env = Env("3.11")
            >>> assert len(env.secrets) == 0  # empty secrets object
        """
        return self._env.secrets

    @secrets.setter
    def secrets(self, value: Sequence[Secret]) -> None:
        """Set the Secrets list-like object for this environment.

        Args:
            value(Sequence[Secret]): The new Secrets list-like object.

        Returns:
            None: This method does not return anything.

        Raises:
            TypeError: If not every element in the value is a Secret object.

        Examples:
            >>> from ev import Env
            >>> env = Env("3.11")
            >>> env.secrets += [Secret.from_pydict({"MY_KEY": "***"})]
            >>> assert len(env.secrets) == 1
        """
        if all(isinstance(s, Secret) for s in value):
            self._env.secrets = list(value)
        else:
            raise TypeError("secrets must be a sequence of Secret objects")

    def _inner_include(self, paths: list[Path]) -> None:
        # TODO(sammy): We should pass Path directly to rust instead of passing strings
        self._env.include([path if isinstance(path, str) else path.as_posix() for path in paths])

    @functools.singledispatchmethod
    def include(self, paths: str | list[str]) -> Env:
        """Adds the given file path to this environment, returning itself for chaining.

        Args:
            paths(str | list[str]): The file path(s) to include. Can be a string path or list of string paths.

        Returns:
            Env: Returns this environment instance for method chaining.

        Raises:
            TypeError: If the paths argument is of an unsupported type.

        Examples:
            >>> env = Env("3.11")
            >>> env.include("/path/to/local.py")
        """
        raise TypeError(f"Unsupported argument type, {type(paths)}")

    @include.register(str)
    def _(self, paths: str) -> Env:
        # The file that the "include" is called from is two frames above the current frame
        # because of the functools.singledispatchmethod decorator.
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            calling_file = frame.f_back.f_back.f_code.co_filename
            calling_dir = pathlib.Path(pathlib.Path(calling_file).resolve()).parent
        else:
            calling_dir = Path.cwd()

        self._inner_include([calling_dir / paths])
        return self

    @include.register(list)
    def _(self, paths: list[str]) -> Env:
        # The file that the "include" is called from is two frames above the current frame
        # because of the functools.singledispatchmethod decorator.
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            calling_file = frame.f_back.f_back.f_code.co_filename
            calling_dir = pathlib.Path(pathlib.Path(calling_file).resolve()).parent
        else:
            calling_dir = Path.cwd()

        joined_paths: list[Path] = [(calling_dir / path) for path in paths]
        self._inner_include(joined_paths)
        return self

    @functools.singledispatchmethod
    def pip_install(self, requirements: str | list[str]) -> Env:
        """Adds the requirements to this environment, returning itself for chaining.

        See: https://pip.pypa.io/en/stable/reference/requirements-file-format/

        Args:
            requirements(str | list[str]): The requirements.txt path (str) or a requirements list.

        Returns:
            Env: Returns this environment instance for method chaining.

        Raises:
            TypeError: If the requirements argument is of an unsupported type.

        Examples:
            >>> env = Env("3.11")
            >>> env.pip_install("daft==0.5.0")
        """
        raise TypeError("Expected either a requirements file path or list of requirements.")

    @pip_install.register(str)
    def _(self, requirements: str) -> Env:
        # get the directory of the calling file to resolve relative paths
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            calling_file = frame.f_back.f_back.f_code.co_filename
            calling_dir = pathlib.Path(pathlib.Path(calling_file).resolve()).parent
        else:
            calling_dir = Path.cwd()
        requirements_path = calling_dir / requirements
        # consider a library, but this will suffice.
        lines = []
        with requirements_path.open() as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    lines.append(stripped_line)

        # adds all the parsed requirements
        self._env.pip_install(lines)
        return self

    @pip_install.register(list)
    def _(self, requirements: list[str]) -> Env:
        self._env.pip_install(requirements)
        return self
