#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""Logging utilities."""

import logging
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

Logger = logging.Logger

LOG = logging.getLogger("geo_dskit")
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)


def with_logger(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator: Provide a default logger or use the provided logger.

    Args:
        func: The function to decorate.

    Returns:
        The decorated function.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger = kwargs.get("logger")
        if logger is None:
            logger = LOG
        kwargs["logger"] = logger
        return func(*args, **kwargs)

    return wrapper
