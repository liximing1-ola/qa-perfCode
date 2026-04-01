#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Query subscription info from Google Play."""
import argparse
import json
import sys

import httplib2
from apiclient.discovery import build
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials


def create_service() -> build:
    """创建 Google Play 服务"""
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'key.json',
        scopes=['https://www.googleapis.com/auth/androidpublisher']
    )
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('androidpublisher', 'v3', http=http)


def query_subscription(
    service,
    package_name: str,
    subscription_id: str,
    token: str
) -> dict:
    """查询订阅信息
    
    :param service: Google Play 服务
    :param package_name: 包名
    :param subscription_id: 订阅 ID
    :param token: 购买令牌
    :return: 订阅信息
    """
    return service.purchases().subscriptions().get(
        packageName=package_name,
        subscriptionId=subscription_id,
        token=token
    ).execute()


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='Query subscription info')
    parser.add_argument('package_name', help='Package name')
    parser.add_argument('subscription_id', help='Subscription ID')
    parser.add_argument('token', help='Purchase token')
    args = parser.parse_args()
    
    try:
        service = create_service()
        
        print(f"Querying subscription: {args.subscription_id}")
        result = query_subscription(
            service,
            args.package_name,
            args.subscription_id,
            args.token
        )
        
        print("\nSubscription info:")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        return 0
        
    except client.AccessTokenRefreshError:
        print("Error: Credentials expired or revoked")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
