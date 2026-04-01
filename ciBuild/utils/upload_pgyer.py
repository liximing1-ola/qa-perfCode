#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒲公英应用上传工具
API 文档: https://www.pgyer.com/doc/view/api#fastUploadApp
"""
import time
from pathlib import Path
from typing import Callable

import requests

# API 错误码
BUILD_PROCESSING = (1246, 1247)  # 应用正在解析/发布中


def get_cos_token(
    api_key: str,
    install_type: int = 2,
    password: str = '',
    update_desc: str = '',
    build_type: str = 'android'
) -> dict | None:
    """获取 COS 上传 Token
    
    :param api_key: API Key
    :param install_type: 1=公开, 2=密码安装, 3=邀请安装
    :param password: 安装密码
    :param update_desc: 更新描述
    :param build_type: ios 或 android
    :return: Token 数据或 None
    """
    url = 'https://www.pgyer.com/apiv2/app/getCOSToken'
    payload = {
        '_api_key': api_key,
        'buildType': build_type,
        'buildInstallType': install_type,
        'buildPassword': password,
        'buildUpdateDescription': update_desc,
    }
    
    try:
        resp = requests.post(url, data=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result.get('data')
    except requests.RequestException as e:
        print(f'获取 Token 失败: {e}')
        return None


def upload_file(file_path: str, upload_url: str, params: dict) -> bool:
    """上传文件到 COS
    
    :param file_path: 本地文件路径
    :param upload_url: 上传 URL
    :param params: 上传参数
    :return: 是否成功
    """
    path = Path(file_path)
    if not path.exists():
        print(f'文件不存在: {file_path}')
        return False
    
    print("上传中...")
    try:
        with open(path, 'rb') as f:
            files = {'file': f}
            resp = requests.post(upload_url, data=params, files=files, timeout=300)
        
        if resp.status_code == 204:
            print("上传成功，正在获取包处理信息...")
            return True
        else:
            print(f'上传失败，HTTP {resp.status_code}')
            return False
    except requests.RequestException as e:
        print(f'上传失败: {e}')
        return False


def get_build_info(api_key: str, build_key: str, max_retries: int = 30) -> dict | None:
    """获取构建信息，轮询直到处理完成
    
    :param api_key: API Key
    :param build_key: 构建 Key
    :param max_retries: 最大重试次数
    :return: 构建信息或 None
    """
    url = 'https://www.pgyer.com/apiv2/app/buildInfo'
    params = {'_api_key': api_key, 'buildKey': build_key}
    
    for attempt in range(max_retries):
        time.sleep(3)
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            
            code = result.get('code')
            if code not in BUILD_PROCESSING:
                return result
            
            print(f"处理中... ({attempt + 1}/{max_retries})")
        except requests.RequestException as e:
            print(f'查询失败: {e}')
    
    print('处理超时')
    return None


def upload_to_pgyer(
    file_path: str,
    api_key: str,
    install_type: int = 2,
    password: str = '',
    update_desc: str = '',
    callback: Callable[[bool, dict | None], None] | None = None,
    build_type: str = 'android'
) -> bool:
    """上传应用到蒲公英
    
    :param file_path: APK/IPA 文件路径
    :param api_key: API Key
    :param install_type: 安装类型
    :param password: 安装密码
    :param update_desc: 更新描述
    :param callback: 回调函数 (success, result)
    :param build_type: 应用类型
    :return: 是否成功
    """
    # 获取上传 Token
    token_data = get_cos_token(api_key, install_type, password, update_desc, build_type)
    if not token_data:
        if callback:
            callback(False, None)
        return False
    
    # 上传文件
    upload_url = token_data['endpoint']
    params = token_data['params']
    
    if not upload_file(file_path, upload_url, params):
        if callback:
            callback(False, None)
        return False
    
    # 获取构建信息
    build_key = params.get('key')
    result = get_build_info(api_key, build_key)
    
    success = result is not None
    if callback:
        callback(success, result)
    
    return success
