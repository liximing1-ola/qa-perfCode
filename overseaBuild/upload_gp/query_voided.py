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

"""Query voided purchases from Google Play."""
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


def query_voided_purchases(service, package_name: str) -> dict:
    """查询已作废的购买
    
    :param service: Google Play 服务
    :param package_name: 包名
    :return: 查询结果
    """
    return service.purchases().voidedpurchases().list(
        packageName=package_name,
        type="1"
    ).execute()


def save_results(data: dict, output_file: str = 'voided.json') -> None:
    """保存结果到文件
    
    :param data: 查询结果
    :param output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Results saved to: {output_file}")


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='Query voided purchases')
    parser.add_argument('package_name', help='Package name, e.g., com.android.sample')
    parser.add_argument('-o', '--output', default='voided.json', help='Output file')
    args = parser.parse_args()
    
    try:
        service = create_service()
        
        print(f"Querying voided purchases for: {args.package_name}")
        result = query_voided_purchases(service, args.package_name)
        
        # 打印结果
        print("\nQuery result:")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        # 保存到文件
        save_results(result, args.output)
        
        return 0
        
    except client.AccessTokenRefreshError:
        print("Error: Credentials expired or revoked")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
