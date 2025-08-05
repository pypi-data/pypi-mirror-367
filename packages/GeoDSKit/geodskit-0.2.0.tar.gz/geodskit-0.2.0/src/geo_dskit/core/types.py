#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

import xarray as xr

if TYPE_CHECKING:
    XarrayData: TypeAlias = xr.Dataset | xr.DataArray
    PathLike: TypeAlias = str | Path

    TypeCMIP: TypeAlias = Literal[
        "variable",
        "frequency",
        "model",
        "experiment",
        "ensemble",
        "grid",
        "year_range",
    ]
