#!/usr/bin/env python3
"""Produce a YAML file with LHCb bookkeeping and production information.

This script queries the LHCb Bookkeeping system to retrieve information about
the logical file names (LFNs) and productions associated with a given
Bookkeeping path. It then formats this information into a JSON file.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import click

logger = logging.getLogger(__name__)


def _dump_yaml(data: object, path: Path, **kwargs: Any) -> None:
    """Dump a Python object to a YAML file.

    This function also logs the path where the YAML file is being saved.

    Args:
        data: The Python object to be dumped to YAML.
        path: The path where the YAML file will be saved.
        **kwargs: Additional keyword arguments to pass to :py:func:`yaml.safe_dump`.
            By default, ``sort_keys`` is set to ``False``.
    """
    from yaml import safe_dump  # noqa: PLC0415

    if not path.parent.exists():
        logger.info("Creating directory: %s", path.parent)
        path.parent.mkdir(parents=True, exist_ok=False)

    logger.debug("Dumping YAML file to '%s'", path)
    kwargs.setdefault("sort_keys", False)
    with path.open("w") as file:
        safe_dump(data, file, **kwargs)


def _setup_basic_logging(level: str) -> None:
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


_LOG_LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


@click.command()
@click.argument("bk_path", type=str, required=True)
@click.argument("output_path", type=Path, required=True)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(_LOG_LEVELS),
    default=_LOG_LEVELS[1],
    help="Set the logging level.",
    is_eager=True,  # run this callback before other options
    expose_value=False,  # we don't need to inject `log_level` into the command
    callback=lambda ctx, param, value: _setup_basic_logging(value),  # noqa: ARG005
    show_default=True,
)
def produce_dirac_info(bk_path: str, output_path: Path) -> None:
    """Produce a YAML file with LHCb bookkeeping and production information.

    The first argument is the path to the LHCb Bookkeeping
    (e.g., /lhcb/MC/2012/ALLSTREAMS.DST/).
    The second argument is the output path for the YAML file.
    """
    from ._dirac import get_bk_info_from_bk_path  # noqa: PLC0415

    output_path = output_path.expanduser().resolve()
    if not (parent_dir := output_path.parent).exists():
        logger.info("Creating directory: %s", parent_dir)
        parent_dir.mkdir(parents=True, exist_ok=False)

    logger.info("Producing LHCb Bookkeeping information for path: %s", bk_path)
    bk_info = get_bk_info_from_bk_path(bk_path)

    _dump_yaml(bk_info.model_dump(mode="json"), output_path)


if __name__ == "__main__":
    produce_dirac_info()
