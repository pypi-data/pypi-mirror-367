#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

import xarray as xr

from geo_dskit.utils.log import LOG, Logger, with_logger

if TYPE_CHECKING:
    from geo_dskit.core.types import PathLike, XarrayData


@with_logger
def write_geo_attrs(
    dataset: XarrayData,
    lat_name: str = "lat",
    lon_name: str = "lon",
    *,
    logger: Logger = LOG,
) -> XarrayData:
    """写入地理属性"""
    dataset[lat_name].attrs["units"] = "degree"
    dataset[lon_name].attrs["units"] = "degree"
    logger.debug("写入地理属性: %s", dataset)
    return dataset


@with_logger
def read_nc(
    path: PathLike,
    variable: Optional[str] = None,
    verbose: bool = False,
    *,
    logger: Logger = LOG,
    **kwargs,
) -> XarrayData:
    """读取nc文件"""
    logger.debug("读取nc文件: %s", path)
    dataset = xr.open_dataset(path, **kwargs)
    if variable:
        dataset = dataset[variable]
    dataset = write_geo_attrs(dataset)
    if verbose:
        logger.debug("Info: %s", dataset.info())
    return dataset


@with_logger
def write_nc(
    data: XarrayData,
    path: PathLike,
    variable: str,
    model: str,
    frequency: str = "mon",
    experiment: str = "past1000",
    ensemble: str = "r1i1p1f1",
    time_range: Optional[str] = None,
    encoding: Optional[dict] = None,
    *,
    logger: Logger = LOG,
    **kwargs,
) -> None:
    """写入nc文件，保持CMIP6命名格式

    Args:
        data: 要写入的数据（Dataset 或 DataArray）
        path: 写入目录
        variable: 变量名（如 'pet', 'pr' 等）
        model: 模型名
        frequency: 时间频率，默认'mon'
        experiment: 实验名，默认'past1000'
        ensemble: 集合名，默认'r1i1p1f1'
        time_range: 时间范围，如'0850-1850'。如果为None则自动从数据中提取
        encoding: 编码设置
        **kwargs: 传递给to_netcdf的其他参数
    """
    path = Path(path)

    # 确保目录存在
    path.mkdir(parents=True, exist_ok=True)

    # 如果没有提供时间范围，从数据中提取
    if time_range is None:
        start_year = int(data.time.dt.year.min().values)
        end_year = int(data.time.dt.year.max().values)
        time_range = f"{start_year:04d}-{end_year:04d}"

    # 构建CMIP格式的文件名
    filename = f"{variable}_{frequency}_{model}_{experiment}_{ensemble}_{time_range}.nc"
    filepath = path / filename

    # 如果是DataArray，转换为Dataset
    if isinstance(data, xr.DataArray):
        data = data.to_dataset(name=variable)

    # 设置默认编码
    if encoding is None:
        encoding = {var: {"zlib": True, "complevel": 4} for var in data.variables}

    # 写入文件
    logger.debug("写入nc文件: %s", filepath)
    data.to_netcdf(filepath, encoding=encoding, **kwargs)
    logger.info("文件已保存: %s", filepath)
