#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Query voided purchases from Google Play."""
import argparse
import json
import sys

from google.auth.exceptions import RefreshError

from gp_utils import create_service


def query_voided_purchases(service, package_name: str, voided_type: str = "1") -> dict:
    """查询已作废的购买"""
    return service.purchases().voidedpurchases().list(
        packageName=package_name,
        type=voided_type
    ).execute()


def save_results(data: dict, output_file: str = 'voided.json') -> None:
    """保存结果到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"结果已保存到：{output_file}")


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='查询 Google Play 已作废购买')
    parser.add_argument('package_name', help='包名，如 com.android.sample')
    parser.add_argument('-o', '--output', default='voided.json', help='输出文件路径')
    parser.add_argument('-k', '--key-file', default='key.json', help='服务账号密钥文件路径')
    parser.add_argument('-t', '--type', default='1', help='作废类型（默认 1）')
    args = parser.parse_args()

    try:
        service = create_service(args.key_file)

        print(f"正在查询已作废购买：{args.package_name}")
        result = query_voided_purchases(service, args.package_name, args.type)

        # 打印结果
        print("\n查询结果：")
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # 保存到文件
        save_results(result, args.output)

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
