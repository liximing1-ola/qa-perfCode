#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信构建通知工具
"""
import argparse
import json
import sys
from dataclasses import dataclass

import requests


@dataclass
class BuildInfo:
    """构建信息"""
    build_num: int
    change_log: str
    build_type: str
    version: str
    platform: str
    ci_num: str
    user: str
    branch: str


class WechatNotifier:
    """企业微信通知器"""
    
    WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'
    MAX_MSG_LEN = 2000
    
    # 构建类型标题模板
    STORE_TITLES = {
        'All': 'app {version} 已上传 Google Play & App Store',
        'iOS': 'app {version} 已上传 App Store',
        'Android': 'app {version} 已上传 Google Play'
    }
    
    STORE_DESCS = {
        'All': 'app {version} 已上传至 Google Play 草稿箱和 TestFlight，注意提审！',
        'iOS': 'app {version} 已上传至 TestFlight，注意提审！',
        'Android': 'app {version} 已上传至 Google Play 草稿箱，注意提审！'
    }
    
    def __init__(self, webhook_key: str):
        self.url = self.WEBHOOK_URL.format(webhook_key)
        self.headers = {'Content-Type': 'application/json'}
    
    def send(self, payload: dict) -> bool:
        """发送消息"""
        try:
            resp = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            print(resp.text)
            return True
        except requests.RequestException as e:
            print(f'发送失败: {e}')
            return False
    
    def send_markdown(self, content: str) -> bool:
        """发送 Markdown 消息"""
        return self.send({
            "msgtype": "markdown",
            "markdown": {"content": content}
        })
    
    def send_build_card(self, info: BuildInfo) -> bool:
        """发送构建卡片消息"""
        # 根据构建类型生成标题和描述
        if info.build_type == "store":
            title = self.STORE_TITLES.get(info.platform, '').format(version=info.version)
            desc = self.STORE_DESCS.get(info.platform, '').format(version=info.version)
            jump_list = []
        elif info.build_type == "channel":
            title = f"app {info.version} 渠道包已打好"
            desc = f"app {info.version} 渠道包已打好，注意分发！"
            jump_list = []
        else:
            title = f"build {info.ci_num} 号包"
            desc = f"{info.build_type} 打好了~~~"
            jump_list = [{
                "type": 1,
                "url": "https://www.pgyer.com/",
                "title": "应用下载地址"
            }]
        
        payload = {
            "msgtype": "template_card",
            "template_card": {
                "card_type": "news_notice",
                "source": {
                    "icon_url": "https://s3.bmp.ovh/imgs/2021/12/6f9a6233af95bb6a.png",
                    "desc": "Partying"
                },
                "main_title": {"title": title, "desc": desc},
                "card_image": {
                    "url": "https://s3.bmp.ovh/imgs/2022/02/0660282ed6d612b9.jpg",
                    "aspect_ratio": 2.0
                },
                "horizontal_content_list": [
                    {"keyname": "Trigger", "value": info.user, "type": 1},
                    {"keyname": "Branch", "value": info.branch, "type": 1}
                ],
                "jump_list": jump_list,
                "card_action": {
                    "type": 1,
                    "url": "https://www.pgyer.com/partying"
                }
            }
        }
        return self.send(payload)
    
    def notify(self, info: BuildInfo) -> bool:
        """根据构建号发送不同类型的通知"""
        # 构建号 < 0: 仅发送变更日志
        if info.build_num < 0:
            return self.send_markdown(info.change_log)
        
        # 构建号 == 0: 发送变更日志 + 触发信息
        if info.build_num == 0:
            content = f"""{info.change_log}
> Trigger: **{info.user}**
> Branch: **{info.branch}**"""
            return self.send_markdown(content)
        
        # 构建号 > 0: 发送构建卡片 + 变更日志
        if not self.send_build_card(info):
            return False
        
        # debug/release 类型额外发送变更日志
        if info.build_type in ('debug', 'release') and info.change_log:
            msg = info.change_log[:self.MAX_MSG_LEN]
            if len(info.change_log) > self.MAX_MSG_LEN:
                msg += '..'
            return self.send_markdown(f"**`最近提交记录：`**\n{msg}")
        
        return True


def parse_args() -> BuildInfo:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='企业微信构建通知')
    parser.add_argument('build_num', type=int, help='构建号')
    parser.add_argument('change_log', help='变更日志')
    parser.add_argument('build_type', help='构建类型')
    parser.add_argument('version', help='版本号')
    parser.add_argument('platform', help='构建平台')
    parser.add_argument('ci_num', help='CI 编号')
    parser.add_argument('user', help='构建用户')
    parser.add_argument('branch', help='构建分支')
    parser.add_argument('--webhook-key', default='', help='企业微信 Webhook Key')
    
    args = parser.parse_args()
    
    return BuildInfo(
        build_num=args.build_num,
        change_log=args.change_log if args.change_log != "no changes" else "",
        build_type=args.build_type,
        version=args.version,
        platform=args.platform,
        ci_num=args.ci_num,
        user=args.user,
        branch=args.branch
    )


def main() -> int:
    """主函数"""
    # 兼容旧版命令行参数格式
    if len(sys.argv) >= 9:
        info = BuildInfo(
            build_num=int(sys.argv[1]),
            change_log=sys.argv[2] if len(sys.argv) > 2 else "",
            build_type=sys.argv[3],
            version=sys.argv[4],
            platform=sys.argv[5],
            ci_num=sys.argv[6],
            user=sys.argv[8],
            branch=sys.argv[9] if len(sys.argv) > 9 else ""
        )
        webhook_key = ''
    else:
        info = parse_args()
        webhook_key = ''
    
    notifier = WechatNotifier(webhook_key)
    success = notifier.notify(info)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
