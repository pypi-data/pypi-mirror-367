# -*- coding: utf-8 -*-
"""************************************************************
# Author: Zeng Shengbo shengbo.zeng@ailingues.com
# Date: 2025-06-26 10:21:02
# LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
# LastEditTime: 2025-06-26 10:22:38
# FilePath: //pycorelibs//network//http_utils.py
# Description: 通用基础工具函数,用于网络请求
                Feature:
                    * 支持 GET / POST 方法;
                    * 支持 params(URL 参数)和 data / json(请求体);
                    * 自动判断是否发送 JSON;
                    * 返回 content + headers + status_code;
                    * 支持 proxies 代理;
                    * 支持 SSL 验证开关;
                    * 自动重试，带指数退避;
                    * 返回统一格式 dict;
                    * 可直接用于生产环境做基础工具函数。
#
# Copyright (c) 2025 by AI Lingues, All Rights Reserved.
**********************************************************"""
from enum import Enum
import aiohttp
import asyncio
import ssl
import requests
import time
import logging
from urllib.parse import urlparse
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


def is_url(s: str) -> bool:
    try:
        result = urlparse(s)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False
    

def fetch_url(
    url: str,
    method: HTTPMethod = HTTPMethod.GET,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    verify_ssl: bool = True,
    proxies: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    强化版通用网络请求函数，适用于复杂场景。

    :param {str} url: 请求地址
    :param method: HTTP 方法，GET / POST
    :param headers: 请求头
    :param params: URL 查询参数
    :param data: 表单请求体(如 application/x-www-form-urlencoded)
    :param json_data: JSON 请求体(如 application/json)
    :param timeout: 超时设置(秒)
    :param max_retries: 最大重试次数
    :param backoff_factor: 指数退避时间因子
    :param verify_ssl: 是否验证 SSL 证书
    :param proxies: 代理设置，如 {'http': 'http://127.0.0.1:8888'}
    :return: 统一响应 dict
    """
    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"[{method}] Attempt {attempt + 1}: {url}")
            response = requests.request(
                method=method.value,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout,
                verify=verify_ssl,
                proxies=proxies,
            )

            if 200 <= response.status_code < 300:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "content": response.text,
                    "headers": dict(response.headers),
                    "error": None,
                }
            else:
                logger.warning(
                    f"Non-success status code: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "content": None,
                    "headers": dict(response.headers),
                    "error": f"HTTP error {response.status_code}",
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            if attempt < max_retries:
                sleep_time = backoff_factor * (2**attempt)
                logger.info(f"Retrying after {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                return {
                    "success": False,
                    "status_code": None,
                    "content": None,
                    "headers": {},
                    "error": str(e),
                }


async def async_fetch_url(
    url: str,
    method: HTTPMethod = HTTPMethod.GET,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    verify_ssl: bool = True,
    proxy: Optional[str] = None,  # aiohttp 仅支持单个代理URL字符串
) -> Dict[str, Any]:
    """
    异步网络请求函数，基础组件。
    : param {str} url :
    : param {str} method :
    : param {Optional} headers :
    : param {*} str :
    : param {Optional} params :
    : param {*} Any :
    : param {Optional} data :
    : param {*} Any :
    : param {*} str :
    : param {Optional} json_data :
    : param {*} Any :
    : param {int} timeout :
    : param {int} max_retries :
    : param {float} backoff_factor :
    : param {bool} verify_ssl :
    : param {Optional} proxy :
    : param {*} aiohttp :
    : return {*} :
    : note:
    : example:
    *
    """

    ssl_context = None if verify_ssl else ssl._create_unverified_context()

    for attempt in range(max_retries + 1):
        try:
            timeout_cfg = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
                async with session.request(
                    method=method.value,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_data,
                    ssl=ssl_context,
                    proxy=proxy,
                ) as resp:
                    text = await resp.text()
                    if 200 <= resp.status < 300:
                        return {
                            "success": True,
                            "status_code": resp.status,
                            "content": text,
                            "headers": dict(resp.headers),
                            "error": None,
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": resp.status,
                            "content": None,
                            "headers": dict(resp.headers),
                            "error": f"HTTP error {resp.status}",
                        }
        except Exception as e:
            logger.error(f"Request attempt {attempt+1} failed: {e}")
            if attempt < max_retries:
                sleep_time = backoff_factor * (2**attempt)
                logger.info(f"Retrying in {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)
            else:
                return {
                    "success": False,
                    "status_code": None,
                    "content": None,
                    "headers": {},
                    "error": str(e),
                }


async def main():
    result = await async_fetch_url(
        url="https://rest.uniprot.org/uniprotkb/P99999.xml",
        method=HTTPMethod.GET.value,
        proxy=None,  # 例如："http://127.0.0.1:7890"
        timeout=5,
        max_retries=2,
    )
    if result["success"]:
        print("请求成功：", result["content"])
    else:
        print("请求失败：", result["error"])


if __name__ == "__main__":
    # asyncio.run(main())
    result = fetch_url(
        url="https://files.rcsb.org/download/6KWY.cif",
        method=HTTPMethod.GET,
        # headers={"Content-Type": "application/json"},
        # json_data={"message": "hello"},
        # proxies={"http": "http://127.0.0.1:8888"},
        max_retries=2,
    )

    if result["success"]:
        print("请求成功：", result["content"])
        with open('tmp.cif','w',encoding='utf8') as f:
            f.write(result["content"])
            f.flush()
        print('写入成功')
    else:
        print("请求失败：", result["error"])
