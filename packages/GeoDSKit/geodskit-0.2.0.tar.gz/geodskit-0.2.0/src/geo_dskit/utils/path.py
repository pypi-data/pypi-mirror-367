#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""This module provides functions for checking and creating directories."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Sequence

from geo_dskit.utils.log import LOG, Logger, with_logger

if TYPE_CHECKING:
    from geo_dskit.core.types import PathLike


@with_logger
def check_data_dir(
    path: Optional[PathLike] = None,
    create: bool = False,
    *,
    logger: Logger = LOG,
) -> Path:
    """Check the data directory, create it if it does not exist.

    Args:
        path: The directory to check.
        create: Whether to create the directory if it does not exist.
        logger: The logger to use.

    Returns:
        The checked directory.
    """
    if path is None:
        path = Path.cwd()
    path = Path(path).resolve()
    # 检查路径是否为目录
    if not path.is_dir():
        if create:
            path.mkdir(parents=True, exist_ok=True)
            msg = f"Create directory: {path}"
            logger.info(msg)
        else:
            msg = f"Directory not found: {path}"
            logger.error(msg)
            raise FileNotFoundError(msg)
    logger.info("Directory %s checked.", path)
    return path


@with_logger
def get_files(
    directory: PathLike,
    iter_subdirs: bool = False,
    wildcard: str = "*",
    at_most: int = 1_000,
    *,
    logger: Logger = LOG,
) -> List[Path]:
    """Get all files in the directory."""
    directory = check_data_dir(directory, create=False, logger=logger)
    if iter_subdirs:
        files = directory.rglob(wildcard)
    else:
        files = directory.glob(wildcard)
    # 只保留文件，过滤掉目录
    files_list = [f for f in files if f.is_file()]
    length = len(files_list)
    if length > at_most:
        raise FileNotFoundError(f"Too many files in {directory}")
    logger.info("Found %d files in %s.", length, directory)
    return files_list


def match_file(
    file_path: PathLike,
    regex_pattern: str | re.Pattern,
) -> bool:
    """Match a file path against a regex pattern.

    Args:
        file_path: The file path to match.
        regex_pattern: The regex pattern to use.

    Returns:
        True if the file path matches the regex pattern, False otherwise.
    """
    if isinstance(regex_pattern, str):
        regex_pattern = re.compile(regex_pattern)
    elif not isinstance(regex_pattern, re.Pattern):
        raise ValueError("regex_pattern must be a string or a re.Pattern")
    if isinstance(file_path, str):
        file_path = Path(file_path)
    elif not isinstance(file_path, Path):
        raise ValueError("file_path must be a string or a Path")
    return regex_pattern.match(file_path.name) is not None


@with_logger
def filter_files(
    file_paths: Sequence[PathLike],
    regex_pattern: str,
    *,
    logger: Logger = LOG,
) -> List[Path]:
    """
    Filter files by regex pattern.

    Args:
        file_paths: A list of file paths.
        regex_pattern: The regex pattern to use.
        logger: The logger to use.

    Returns:
        A list of file paths.
    """
    regex = re.compile(regex_pattern)
    matching_files = [Path(fp) for fp in file_paths if match_file(fp, regex)]
    length = len(matching_files)
    logger.info("Found %d files matching the pattern.", length)
    return matching_files
