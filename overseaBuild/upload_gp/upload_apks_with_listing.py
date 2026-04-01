#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License");
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

"""Uploads apk to alpha track and updates its listing properties."""
import argparse
import mimetypes
import socket
import sys
from pathlib import Path

import httplib2
from apiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

from google_translater import GoogleTranslator, TranslationError

# 设置超时和 MIME 类型
socket.setdefaulttimeout(7 * 24 * 60 * 60)
mimetypes.add_type("application/octet-stream", ".apk")
mimetypes.add_type("application/octet-stream", ".aab")

# 发布轨道
TRACK_PRODUCTION = 'production'

# 支持的语言列表
SUPPORTED_LANGUAGES = [
    'en-SG', 'en-AU', 'en-CA', 'en-GB', 'en-IN', 'en-US', 'en-ZA',
    'ar', 'id', 'ko-KR', 'ms', 'ms-MY', 'th', 'tr-TR', 'vi',
    'zh-TW', 'zh-CN', 'zh-HK'
]


def create_release_notes(base_note: str, translator: GoogleTranslator) -> list[dict]:
    """创建多语言发布说明
    
    :param base_note: 基础说明（英文）
    :param translator: 翻译器
    :return: 多语言说明列表
    """
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
            print(f"Error: {lang} text too long ({len(note['text'])} > 500)")
            sys.exit(1)
        
        release_notes.append(note)
    
    return release_notes


def upload_bundle(service, package_name: str, apk_file: str) -> dict:
    """上传 AAB 文件
    
    :param service: Google Play 服务
    :param package_name: 包名
    :param apk_file: AAB 文件路径
    :return: 上传结果
    """
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
    release_notes: list[dict]
) -> None:
    """更新发布轨道
    
    :param service: Google Play 服务
    :param package_name: 包名
    :param version_code: 版本号
    :param draft_name: 草稿名称
    :param release_notes: 发布说明
    """
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']
    
    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=TRACK_PRODUCTION,
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


def create_service() -> build:
    """创建 Google Play 服务"""
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'key.json',
        scopes=['https://www.googleapis.com/auth/androidpublisher']
    )
    http = httplib2.Http()
    http.redirect_codes = http.redirect_codes - {308}
    http = credentials.authorize(http)
    
    return build('androidpublisher', 'v3', http=http)


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='Upload APK/AAB to Google Play')
    parser.add_argument('package_name', help='Package name, e.g., com.android.sample')
    parser.add_argument('apk_file', nargs='?', default='', help='APK/AAB file path')
    parser.add_argument('draft_name', nargs='?', default='最新版', help='Draft name')
    parser.add_argument('release_note', nargs='?', default='', help='Release notes (English)')
    args = parser.parse_args()
    
    # 验证文件
    if args.apk_file and not Path(args.apk_file).exists():
        print(f"Error: File not found: {args.apk_file}")
        return 1
    
    try:
        # 创建服务
        service = create_service()
        
        # 上传文件
        if args.apk_file:
            print("Uploading bundle...")
            response = upload_bundle(service, args.package_name, args.apk_file)
            version_code = response['versionCode']
        else:
            print("Warning: No file to upload")
            return 0
        
        # 翻译并更新发布说明
        if args.release_note:
            print("\nTranslating release notes...")
            translator = GoogleTranslator()
            release_notes = create_release_notes(args.release_note, translator)
            
            print("\nUpdating track...")
            update_track(
                service,
                args.package_name,
                version_code,
                args.draft_name,
                release_notes
            )
        
        print("\nDone!")
        return 0
        
    except client.AccessTokenRefreshError:
        print("Error: Credentials expired or revoked")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
