#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from geo_dskit.utils.log import LOG, Logger, with_logger

if TYPE_CHECKING:
    from geo_dskit.core.types import PathLike


@with_logger
def find_first_uncommented_line(
    file_path: PathLike,
    comment_chars: str = "#",
    encoding: str = "utf-8",
    *,
    logger: Logger = LOG,
) -> int:
    """Find the line number of the first uncommented line (starting from 1).

    Args:
        file_path: The file path.
        comment_chars: The comment characters.
        encoding: The encoding of the file.

    Returns:
        The line number of the first uncommented line (starting from 1).
        If not found, return -1.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not isinstance(file_path, Path):
        raise TypeError(f"The file_path must be a Path, but got {type(file_path)}.")
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    # 是文件路径，逐行读取
    with open(file_path, "r", encoding=encoding) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith(comment_chars):
                return i
    logger.warning("No uncommented line found.")
    return -1


def check_tab_sep(filepath: PathLike, header_lines: int = 5) -> bool:
    """Check if the file is tab separated.

    Args:
        filepath: The file path.

    Returns:
        True if the file is tab separated, False otherwise.
    """
    path = Path(filepath).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"The path '{path}' is not a file.")
    with open(path, "r", encoding="utf-8") as f:
        first_lines = []
        for _ in range(header_lines):
            try:
                first_lines.append(next(f))
            except StopIteration:
                break
    return any("\t" in line for line in first_lines)
