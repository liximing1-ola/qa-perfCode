#! /usr/bin/env python3
# -*- coding:UTF-8 -*-（添加）
import sys
import requests
import json

buildNum = sys.argv[1]
changeLog = "no changes"
buildType = sys.argv[3]
versionName = sys.argv[4]
buildPlatform = sys.argv[5]
buildInfo = sys.argv[6]
ciNum = sys.argv[7]
buildUser = sys.argv[8]
buildBranch = sys.argv[9]

url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'.format('')
headers = {
    'Content-Type': 'application/json'
}

if int(buildNum) < 0:
    changeLog = "" + sys.argv[2]
    logValues = {
        "msgtype": "markdown",
        "markdown": {
            "content": changeLog
        }
    }
    logResponse = requests.post(url, data=json.dumps(logValues), headers=headers)
    print(logResponse.text)
elif int(buildNum) == 0:
    changeLog = "" + sys.argv[2]
    logValues = {
        "msgtype": "markdown",
        "markdown": {
            "content": f'''{changeLog}
            > Trigger: **{buildUser}**
            > Branch: **{buildBranch}** '''
        }
    }
    logResponse = requests.post(url, data=json.dumps(logValues), headers=headers)
    print(logResponse.text)
else:
    jump_list = []
    android_jump = {
        "type": 1,
        "url": "https://www.pgyer.com/",
        "title": "Android包下载地址"
    }
    ios_jump = {
        "type": 1,
        "url": "https://www.pgyer.com/",
        "title": "iOS包下载地址"
    }
    all_jum = {
        "type": 1,
        "url": "https://www.pgyer.com/",
        "title": "应用下载地址"
    }
    if buildPlatform == "All":
        jump_list.append(all_jum)
    elif buildPlatform == "Android":
        jump_list.append(all_jum)
    else:
        jump_list.append(all_jum)

    title = f"build {ciNum} 号包"
    description = f"{buildType}打好了~~~"
    articlesUrl = "https://www.pgyer.com/app"

    if buildType == "store":
        titleDict = {'All': f"app {versionName} 已上传Google Play & App Store",
                     'iOS': f"app {versionName} 已上传App Store",
                     'Android': f"app {versionName} 已上传Google Play"}
        title = titleDict[buildPlatform]
        descDict = {'All': f"app {versionName} 已上传至Google Play 草稿箱和 TestFlight，注意提审！",
                    'iOS': f"app {versionName} 已上传至TestFlight，注意提审！",
                    'Android': f"app {versionName} 已上传至Google Play 草稿箱，注意提审！"}
        description = descDict[buildPlatform]
        jump_list = []
    elif buildType == "channel":
        title = f"app {versionName} 渠道包已打好"
        description = f"app {versionName} 渠道包已打好，注意分发！"
        articlesUrl = f"https://dl.1dmy.com/apk/pt-channel-{versionName}-{buildNum}/"
        jump_list = []

    values = {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "news_notice",
            "source": {
                "icon_url": "https://s3.bmp.ovh/imgs/2021/12/6f9a6233af95bb6a.png",
                "desc": "Partying"
            },
            "main_title": {
                "title": title,
                "desc": description
            },
            "card_image": {
                "url": "https://s3.bmp.ovh/imgs/2022/02/0660282ed6d612b9.jpg",
                "aspect_ratio": 2.0
            },
            "vertical_content_list": [
            ],
            "horizontal_content_list": [
                {
                    "keyname": "Trigger",
                    "value": buildUser,
                    "type": 1,
                    "url": "https://www.pgyer.com/partying"
                },
                {
                    "keyname": "Branch",
                    "value": buildBranch,
                    "type": 1,
                    "url": "https://www.pgyer.com/partying"
                }
            ],
            "jump_list": jump_list,
            "card_action": {
                "type": 1,
                "url": "https://www.pgyer.com/partying",
                "appid": "APPID",
                "pagepath": "PAGEPATH"
            }
        }
    }

    response = requests.post(url, data=json.dumps(values), headers=headers)
    print(response.text)

    if buildType == 'debug' or buildType == 'release':
        if len(sys.argv) > 2 and len(sys.argv[2]) > 0:
            changeLog = "" + sys.argv[2]
        # max-length of wecom msg contenxt is 2048
        msg = (changeLog[:2000] + '..') if len(changeLog) > 2000 else changeLog
        logValues = {
            "msgtype": "markdown",
            "markdown": {
                "content": "**`最近提交记录：`**\n" + msg
            }
        }
        logResponse = requests.post(url, data=json.dumps(logValues), headers=headers)
        print(logResponse.text)
