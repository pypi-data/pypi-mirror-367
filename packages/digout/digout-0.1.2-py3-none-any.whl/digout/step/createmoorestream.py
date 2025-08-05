"""Define a step to create a ``MooreStream`` from a bookkeeping path."""

from __future__ import annotations

import shutil
import sys
from contextlib import contextmanager, nullcontext
from importlib.resources import as_file, files
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from digout._utils.resources import get_add_to_pythonpath_script

from .._utils.ioyaml import load_yaml
from .._utils.path import ResolvedPath  # noqa: TC001
from ..bookkeeping._info import BKInfo
from ..context import Context
from ..core.step import NotRunError, StepKey, StepKind
from ..environment import Environment, execute
from ..stream.moore import MooreStream
from .base import StepBase
from .selector import Selector  # noqa: TC001 (needed by Pydantic)

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping

    from ..context import Context

logger = getLogger(__name__)

__all__ = ["CreateMooreStreamStep"]


@contextmanager
def _get_bookkeeping_package() -> Generator[Path, None, None]:
    """Get the `digout.bookkeeping` package as `_digout_bookkeeping` in a temp dir."""
    with (
        TemporaryDirectory() as temp_dir_,
        as_file(files("digout.bookkeeping")) as bookkeeping_directory,
    ):
        temp_dir = Path(temp_dir_)
        # Copy the bookkeeping package to a temporary directory
        shutil.copytree(
            bookkeeping_directory,
            temp_dir / "_digout_bookkeeping",
            dirs_exist_ok=False,
        )
        logger.debug("Copied bookkeeping package to '%s'", temp_dir)
        yield temp_dir


@contextmanager
def _get_bookkeeping_args(
    input_path: str, output_path: str, *, with_external_env: bool
) -> Generator[list[str], None, None]:
    """Get the arguments to run the bookkeeping script.

    Args:
        input_path: The path to the input file (bookkeeping path).
        output_path: The path where the output YAML file will be saved.
        with_external_env:
            If True, the bookkeeping package is copied to a temporary directory
            and added to the PYTHONPATH.

    Yields:
        A list of command-line arguments to run the bookkeeping script.

    """
    # Get the bookkeeping package in a temporary directory
    with (
        # Get the bookkeeping package in a temporary directory
        # if we are using an external environment
        # so that we can add it to the PYTHONPATH
        _get_bookkeeping_package() if with_external_env else nullcontext()
    ) as bookkeeping_dir:
        # Add the `bookkeeping_dir` to the PYTHONPATH
        # so that the script can find the `digout.bookkeeping` package
        # renamed as `_digout_bookkeeping` (just in case)
        if bookkeeping_dir is not None:
            # Add the environment's Python path to the command
            args = [
                get_add_to_pythonpath_script().as_posix(),
                bookkeeping_dir.as_posix(),
            ]
            logger.debug(
                "Added bookkeeping package to PYTHONPATH: %s",
                bookkeeping_dir,
            )
        else:
            args = []

        # Use python executable from the environment
        # or the system Python interpreter if no environment is provided
        args.extend(
            ["/usr/bin/env", "python3"] if with_external_env else [sys.executable]
        )

        args.extend(
            [
                "-m",
                (
                    "_digout_bookkeeping.produce"
                    if with_external_env
                    else "digout.bookkeeping.produce"
                ),
                input_path,
                output_path,
            ]
        )
        yield args


class CreateMooreStreamStep(StepBase[MooreStream]):
    """Creates a :py:class:`~digout.stream.moore.MooreStream` from a DIRAC bookkeeping path.

    This step runs an external script to query a given bookkeeping path,
    resolving it into a list of Logical File Names (LFNs) and associated Moore
    options.

    It saves this information to an intermediate YAML file and then
    constructs a :py:class:`~digout.stream.moore.MooreStream` object from it.
    """  # noqa: E501

    input: str
    """The DIRAC bookkeeping path to query for data files."""

    output: ResolvedPath
    """Path where the bookkeeping information (as a YAML file) will be saved."""

    environment: Environment | None = None
    """The environment in which to run the bookkeeping query script."""

    select: Selector | None = None
    """An optional selector to filter the list of files retrieved from bookkeeping."""

    n_files_per_chunk: Annotated[int, Field(ge=1)] | None = 1
    """The number of files to group into each chunk in the final :py:class:`~digout.stream.moore.MooreStream`.

    If ``None``, all files are placed into a single chunk.
    """  # noqa: E501

    # Private methods ================================================================
    def _execute(self) -> None:
        """Run the external script to produce the bookkeeping info YAML file."""
        with _get_bookkeeping_args(
            input_path=self.input,
            output_path=self.output.as_posix(),
            with_external_env=self.environment is not None,
        ) as args:
            execute(
                args,
                environment=self.environment,
                # Redirect stdout and stderr to the proper streams
                # since they might be redirected in the `run` method
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

    # Implementation of StepBase =====================================================
    def _has_run(self, _: Context, /) -> bool:
        """Check if the step is complete by looking for the output YAML file."""
        return self.output.exists()

    def _run(self, _: Mapping[StepKey, object], context: Context, /) -> MooreStream:
        """Run the bookkeeping query script and returns the resulting stream."""
        self._execute()
        return self.get_target(context)

    @classmethod
    def get_key(cls) -> str:
        """Return the key for this step, ``create_moore_stream``."""
        return "create_moore_stream"

    def get_source_keys(self) -> set[str]:
        """Return the set of step keys this step depends on.

        :py:class:`generate_grid_proxy <digout.step.generategridproxy.GenerateGridProxyStep>`
        """  # noqa: E501
        return {"generate_grid_proxy"}

    @property
    def kind(self) -> StepKind:
        """:py:attr:`~digout.core.step.StepKind.STREAM`."""
        return StepKind.STREAM

    @classmethod
    def get_stream_type(cls) -> type[MooreStream]:
        """Return the type of stream produced by this step.

        This is :py:class:`~digout.stream.moore.MooreStream`.
        """
        return MooreStream

    def get_target(self, context: Context, /) -> MooreStream:  # noqa: ARG002
        """Load the generated YAML file and constructs the ``MooreStream`` object.

        This method reads the :py:attr:`output` YAML file,
        applies the optional :py:attr:`select` selector, and returns a fully
        configured :py:class:`~digout.stream.moore.MooreStream` instance.

        Args:
            context: The current workflow execution context.

        Returns:
            The final :py:class:`~digout.stream.moore.MooreStream` object.

        Raises:
            NotRunError: If the intermediate :py:attr:`output` file does not exist.
        """
        output_path = self.output
        if not output_path.exists():
            msg = (
                f"The step {self.get_key()} needs to be run first "
                "to produce the target stream."
            )
            raise NotRunError(msg)

        bk_info = BKInfo.model_validate(load_yaml(output_path))
        paths = ["LFN:" + lfn for lfn in bk_info.lfns]

        if (selector := self.select) is not None:
            logger.debug(
                "Applying selector %s to the %d paths in the stream.",
                selector,
                len(paths),
            )
            paths = selector.select(paths)
            logger.debug(
                "After applying the selector, the stream contains %d paths.",
                len(paths),
            )

        return MooreStream(
            paths=paths,
            moore_options=bk_info.get_moore_options(),
            n_files_per_chunk=self.n_files_per_chunk,
        )
