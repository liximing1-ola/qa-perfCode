#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Query subscription info from Google Play."""
import argparse
import json
import sys

from google.auth.exceptions import RefreshError

from gp_utils import create_service


def query_subscription(
    service,
    package_name: str,
    subscription_id: str,
    token: str
) -> dict:
    """查询订阅信息"""
    return service.purchases().subscriptions().get(
        packageName=package_name,
        subscriptionId=subscription_id,
        token=token
    ).execute()


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='查询 Google Play 订阅信息')
    parser.add_argument('package_name', help='包名')
    parser.add_argument('subscription_id', help='订阅 ID')
    parser.add_argument('token', help='购买令牌')
    parser.add_argument('-k', '--key-file', default='key.json', help='服务账号密钥文件路径')
    args = parser.parse_args()

    try:
        service = create_service(args.key_file)

        print(f"正在查询订阅：{args.subscription_id}")
        result = query_subscription(
            service,
            args.package_name,
            args.subscription_id,
            args.token
        )

        print("\n订阅信息：")
        print(json.dumps(result, indent=4, ensure_ascii=False))

        return 0

    except RefreshError:
        print("错误：凭证已过期或被撤销")
        return 1
    except FileNotFoundError as e:
        print(f"错误：密钥文件不存在：{e}")
        return 1
    except Exception as e:
        print(f"错误：{e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
