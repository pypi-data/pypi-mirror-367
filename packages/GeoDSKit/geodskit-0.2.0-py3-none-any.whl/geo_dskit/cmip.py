#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Handle datasets downloaded from CMIP."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import click

from geo_dskit.utils.log import LOG, Logger, with_logger
from geo_dskit.utils.path import filter_files, get_files

if TYPE_CHECKING:
    from geo_dskit.core.types import PathLike


@dataclass
class CMIPComponents:
    """CMIP file components."""

    variable: str
    frequency: str
    model: str
    experiment: str
    ensemble: str
    grid: Optional[str] = None
    year_range: Optional[str] = None

    @classmethod
    def from_filename(cls, filename: str, **kwargs) -> "CMIPComponents":
        """Parse CMIP components from a filename."""
        pattern = re.compile(create_cmip_regex(**kwargs), re.VERBOSE)
        match = pattern.match(filename)
        if not match:
            raise ValueError(f"Invalid CMIP filename: {filename}")
        return cls(**match.groupdict())


@with_logger
def create_cmip_regex(*, logger: Logger = LOG, **kwargs) -> str:
    """Create a regex pattern for CMIP file names.

    Args:
        **kwargs: Keyword arguments to pass to the regex pattern.

    Returns:
        A regex pattern for CMIP file names.
    """
    patterns = {
        "variable": r"\w+",
        "frequency": r"\w+",
        "model": r"[\w-]+",
        "experiment": r"\w+",
        "ensemble": r"r\d+i\d+p\d+f\d+",
        "grid": r"gn|gr\d*|fx",
        "year_range": r"\d+-\d+",
    }

    # Update user-specified patterns
    for k, v in kwargs.items():
        if k in patterns and v is not None:  # 只处理非 None 值
            patterns[k] = re.escape(v)

    # Build the basic regex
    template = (
        r"^(?P<variable>{variable})_"
        r"(?P<frequency>{frequency})_"
        r"(?P<model>{model})_"
        r"(?P<experiment>{experiment})_"
        r"(?P<ensemble>{ensemble})"
        r"(?:_(?P<grid>{grid}))?_"  # Keep grid part optional
        r"(?P<year_range>{year_range})"
        r"\.nc$"
    )

    # If grid is specified, modify the grid part of the template
    if "grid" in kwargs:
        template = template.replace(
            r"(?:_(?P<grid>{grid}))?_",
            r"_(?P<grid>{grid})_",  # When grid is specified, it must match
        )

    logger.debug("Created CMIP regex pattern: %s", template)
    return template.format(**patterns)


@with_logger
def get_cmip_files(
    data_dir: PathLike,
    iter_subdirs: bool = False,
    *,
    logger: Logger = LOG,
    **kwargs,
) -> List[Path]:
    """Get paths of CMIP files from a directory.

    Args:
        data_dir: The directory to search for CMIP files.
        iter_subdirs: Whether to iterate over subdirectories.
        **kwargs: Keyword arguments to pass to the regex pattern.

    Returns:
        A list of paths to CMIP files.
    """
    pattern = create_cmip_regex(logger=logger, **kwargs)
    paths = get_files(data_dir, iter_subdirs=iter_subdirs, logger=logger)
    selected_files = filter_files(paths, pattern, logger=logger)
    if not selected_files:
        logger.warning("No files found matching the pattern.")
    return selected_files


@click.command()
@click.argument("path", type=click.Path(exists=False), default=None)
@click.option("--model", "-m", type=str, help="model name")
@click.option("--variable", "-v", type=str, help="variable name")
@click.option("--frequency", "-f", type=str, help="frequency")
@click.option("--experiment", "-e", type=str, help="experiment name")
@click.option("--ensemble", "-n", type=str, help="ensemble name")
@click.option("--verbose", is_flag=True, help="show detailed information")
@click.option("--iter-subdirs", "-r", is_flag=True, help="iterate over subdirectories")
def cli(
    path: PathLike = Path.cwd(),
    model: Optional[str] = None,
    variable: Optional[str] = None,
    frequency: Optional[str] = None,
    experiment: Optional[str] = None,
    ensemble: Optional[str] = None,
    verbose: bool = False,
    iter_subdirs: bool = False,
):
    """Search CMIP files.

    PATH: The path to search for CMIP files.
    """
    params = {
        "model": model,
        "variable": variable,
        "frequency": frequency,
        "experiment": experiment,
        "ensemble": ensemble,
    }
    LOG.info("🔍 Searching CMIP files...")
    for name, value in params.items():
        if value:
            LOG.info(
                "➕ searching %s: %s",
                name,
                value,
                extra=params,
            )
    files = get_cmip_files(
        path,
        model=model,
        variable=variable,
        frequency=frequency,
        experiment=experiment,
        ensemble=ensemble,
        iter_subdirs=iter_subdirs,
    )
    if verbose:
        for file in files:
            LOG.info(file)
    LOG.info("Found %d files", len(files))


if __name__ == "__main__":
    cli()
