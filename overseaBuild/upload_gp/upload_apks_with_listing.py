#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload APK/AAB to Google Play and update listing properties."""
import argparse
import mimetypes
import socket
import sys
from pathlib import Path

from google.auth.exceptions import RefreshError
from googleapiclient.http import MediaFileUpload

from gp_utils import create_service
from google_translater import GoogleTranslator, TranslationError

# 上传超时（7天，Google Play 大文件上传需要较长超时）
UPLOAD_TIMEOUT_SECONDS = 7 * 24 * 60 * 60

# 设置超时和 MIME 类型
socket.setdefaulttimeout(UPLOAD_TIMEOUT_SECONDS)
mimetypes.add_type("application/octet-stream", ".apk")
mimetypes.add_type("application/octet-stream", ".aab")

# 支持的语言列表
SUPPORTED_LANGUAGES = [
    'en-SG', 'en-AU', 'en-CA', 'en-GB', 'en-IN', 'en-US', 'en-ZA',
    'ar', 'id', 'ko-KR', 'ms', 'ms-MY', 'th', 'tr-TR', 'vi',
    'zh-TW', 'zh-CN', 'zh-HK'
]


def create_release_notes(base_note: str, translator: GoogleTranslator) -> list[dict]:
    """创建多语言发布说明。"""
    if not base_note:
        return []

    release_notes = []

    for lang in SUPPORTED_LANGUAGES:
        note = {'language': lang, 'text': ''}

        try:
            if lang.startswith('en'):
                note['text'] = base_note
            elif '-' in lang:
                base_lang = lang.split('-')[0]
                # 繁体中文特殊处理
                if base_lang == 'zh' and lang != 'zh-CN':
                    note['text'] = translator.translate(base_note, 'zh-TW')
                else:
                    note['text'] = translator.translate(base_note, base_lang)
            else:
                note['text'] = translator.translate(base_note, lang)
        except TranslationError as e:
            print(f"Warning: Failed to translate to {lang}: {e}")
            note['text'] = base_note

        # 检查长度限制
        if len(note['text']) > 500:
            raise ValueError(f"{lang} release note too long ({len(note['text'])} > 500 chars)")

        release_notes.append(note)

    return release_notes


def upload_bundle(service, package_name: str, apk_file: str) -> dict:
    """上传 AAB 文件。"""
    # 创建编辑
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    # 准备上传
    media = MediaFileUpload(apk_file, chunksize=1024*1024, resumable=True)
    request = service.edits().bundles().upload(
        editId=edit_id,
        ackBundleInstallationWarning=True,
        packageName=package_name,
        media_body=media
    )

    # 上传并显示进度
    response = None
    spinner = ['—', '\\', '|', '/']

    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            bar = "█" * (progress // 2)
            symbol = spinner[(progress - 1) % 4]
            sys.stdout.write(f"\r[{symbol}]{progress:3d}%|{bar}| {progress}/100")
            sys.stdout.flush()

    print(f"\nVersion code {response['versionCode']} uploaded")

    # 提交编辑
    service.edits().commit(editId=edit_id, packageName=package_name).execute()

    return response


def update_track(
    service,
    package_name: str,
    version_code: int,
    draft_name: str,
    release_notes: list[dict],
    track: str = 'production'
) -> None:
    """更新发布轨道。"""
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package_name,
        body={
            'releases': [{
                'name': f'{draft_name} draft',
                'versionCodes': [version_code],
                'status': 'draft',
                'releaseNotes': release_notes
            }]
        }
    ).execute()

    print(f"Track {track_response['track']} updated")

    service.edits().commit(editId=edit_id, packageName=package_name).execute()
    print("Release notes committed")


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='上传 APK/AAB 到 Google Play')
    parser.add_argument('package_name', help='包名，如 com.android.sample')
    parser.add_argument('apk_file', nargs='?', default='', help='APK/AAB 文件路径')
    parser.add_argument('draft_name', nargs='?', default='最新版', help='草稿名称')
    parser.add_argument('release_note', nargs='?', default='', help='发布说明（英文）')
    parser.add_argument('-k', '--key-file', default='key.json', help='服务账号密钥文件路径')
    parser.add_argument('--track', default='production', help='发布轨道（默认 production）')
    args = parser.parse_args()

    # 验证文件
    if args.apk_file and not Path(args.apk_file).exists():
        print(f"错误：文件不存在：{args.apk_file}")
        return 1

    try:
        # 创建服务
        service = create_service(args.key_file)

        # 上传文件
        if args.apk_file:
            print("正在上传 bundle...")
            response = upload_bundle(service, args.package_name, args.apk_file)
            version_code = response['versionCode']
        else:
            print("Warning: No file to upload")
            return 0

        # 翻译并更新发布说明
        if args.release_note:
            print("\n正在翻译发布说明...")
            translator = GoogleTranslator()
            release_notes = create_release_notes(args.release_note, translator)

            print("\n正在更新 track...")
            update_track(
                service,
                args.package_name,
                version_code,
                args.draft_name,
                release_notes,
                args.track
            )

        print("\n完成！")
        return 0

    except RefreshError:
        print("错误：凭证已过期或被撤销")
        return 1
    except ValueError as e:
        print(f"错误：{e}")
        return 1
    except FileNotFoundError as e:
        print(f"错误：密钥文件不存在：{e}")
        return 1
    except Exception as e:
        print(f"错误：{e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())