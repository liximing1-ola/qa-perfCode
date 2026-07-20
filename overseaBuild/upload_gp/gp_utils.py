#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Google Play API 共享工具"""
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Play Developer API .scope
SCOPE = 'https://www.googleapis.com/auth/androidpublisher'

# API 版本
API_VERSION = 'v3'

# 服务名称
API_NAME = 'androidpublisher'


def create_service(key_path: str = 'key.json'):
    """创建 Google Play Developer API 服务"""
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=[SCOPE]
    )
    return build(API_NAME, API_VERSION, credentials=credentials)
