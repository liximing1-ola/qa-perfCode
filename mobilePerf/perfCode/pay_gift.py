#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
礼物赠送测试脚本

用于测试私聊送礼和房间送礼功能
"""
from random import random, randrange
import json
import os
import traceback

import requests
import urllib3
from typing import List

# 服务器地址（直接在此修改）
BASE_URL = 'https://114.55.3.96'

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_token(uid: int) -> str:
    """获取用户 token
    
    :param uid: 用户 ID
    :return: token 字符串
    :raises ValueError: 获取 token 失败时
    """
    url = f"{BASE_URL}/test/userToken?uid={uid}"
    
    response = requests.get(url, verify=False)
    response.raise_for_status()
    
    data = response.json()
    if 'data' not in data:
        raise ValueError(f"获取 token 失败: {data}")
    
    return data['data']


def pay_chat(to_uid: int, num: int = 1, gift_id: int = 545, price: int = 10, uid: int = 200254964) -> dict:
    """私聊送礼
    
    :param to_uid: 接收者 UID
    :param num: 礼物数量
    :param gift_id: 礼物 ID
    :param price: 礼物单价
    :param uid: 发送者 UID
    :return: 响应数据
    """
    token = get_token(uid)
    money = num * price
    
    url = f"{BASE_URL}/pay/create"
    params = {
        "package": "com.yhl.sleepless.android",
        "_ipv": "0",
        "_platform": "android",
        "_index": "198",
        "_model": "22041216C",
        "_timestamp": "1743560586",
        "format": "json",
        "_sign": "5ebc2012a4d5e8663200ea4d5fbec64e"
    }
    
    gift_params = {
        "notify_group_id": 0,
        "to": to_uid,
        "giftId": gift_id,
        "giftNum": num,
        "cid": 0,
        "ctype": "",
        "duction_money": 0,
        "version": 2,
        "num": num,
        "gift_type": "normal",
        "star": 0,
        "show_pac_man_guide": 1,
        "all_mic": 0,
        "valid_all_mic": 0,
        "gift_tab": "gift"
    }
    
    payload = {
        "platform": "available",
        "type": "chat-gift",
        "money": money,
        "params": json.dumps(gift_params)
    }
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; 22041216C Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 Mobile Safari/537.36 / Xs android V5.37.0.0 / Js V1.0.0.0 / Login V1736852068',
        'user-brand': 'Redmi',
        'user-model': '22041216C',
        'user-tag': '3299135d51c6a8ee',
        'user-idfa': '',
        'user-mac': '3299135d51c6a8ee',
        'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        'user-channel': 'slp',
        'user-oaid': '017d5cce25c04e02',
        'user-issimulator': 'false',
        'user-machine': '22041216C',
        'user-did': 'DU2MnBVXQ1l6p_rnQH02rwzzHUF2Gn0oyEaf',
        'user-isroot': 'false',
        'host': BASE_URL.replace('https://', '').replace('http://', ''),
        'user-token': token,
        'user-imei': '3299135d51c6a8ee',
        'user-language': 'zh_CN'
    }
    
    response = requests.post(url, params=params, headers=headers, data=payload, verify=False)
    response.raise_for_status()
    
    result = response.json()
    print(f"私聊送礼结果: {result}")
    return result


def pay_room(to_uid: List[int], gift_num: int = 1, gift_id: int = 211118, 
             price: int = 10, uid: int = 200253117, rid: int = 100504618) -> dict:
    """房间送礼
    
    :param to_uid: 接收者 UID 列表
    :param gift_num: 每人礼物数量
    :param gift_id: 礼物 ID
    :param price: 礼物单价
    :param uid: 发送者 UID
    :param rid: 房间 ID
    :return: 响应数据
    """
    token = get_token(uid)
    money = gift_num * price * len(to_uid)
    
    url = f"{BASE_URL}/pay/create"
    params = {
        "package": "com.yhl.sleepless.android",
        "_ipv": "0",
        "_platform": "android",
        "_index": "133",
        "_model": "PDAM10",
        "_timestamp": "1760414447",
        "format": "json",
        "_sign": "7b24a480b8bae3f35d3eae9880b727d6"
    }
    
    to_uid_str = ','.join(map(str, to_uid))
    positions = ','.join(str(i + 1) for i in range(len(to_uid)))
    num = gift_num * len(to_uid)
    
    gift_params = {
        "is_tora_gift": False,
        "rid": rid,
        "uids": to_uid_str,
        "positions": positions,
        "position": -1,
        "giftId": gift_id,
        "giftNum": gift_num,
        "price": price,
        "cid": 0,
        "ctype": "",
        "duction_money": 0,
        "version": 2,
        "num": num,
        "gift_type": "normal",
        "star": 0,
        "show_pac_man_guide": 1,
        "refer": "/:room",
        "all_mic": 0,
        "valid_all_mic": 0,
        "seats_user": json.dumps({"mic": [0,0,0,0,0,0,0,0,0], "boss": []}),
        "gift_tab": "family",
        "gift_refer": "",
        "clone_id": 0
    }
    
    payload = {
        "platform": "available",
        "type": "package",
        "money": money,
        "params": json.dumps(gift_params)
    }
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; PDAM10 Build/RKQ1.200903.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 / Xs android V5.50.0.0 / Js V1.0.0.0 / Login V1741677935',
        'user-brand': 'OPPO',
        'user-model': 'PDAM10',
        'user-tag': '2845cd497cd7695e',
        'user-idfa': '',
        'user-mac': '2845cd497cd7695e',
        'content-type': 'application/x-www-form-urlencoded',
        'user-channel': 'slp',
        'user-oaid': '9A1B40843973470ABB2F6623C6B8B20130a044983298cfb5a9726c149f980195',
        'user-issimulator': 'false',
        'user-machine': 'PDAM10',
        'user-did': 'DUcqnoi0lkCSzptdyOOGKmNOpxQ8_AeLasc2',
        'user-isroot': 'false',
        'host': BASE_URL.replace('https://', '').replace('http://', ''),
        'user-token': token,
        'user-imei': '2845cd497cd7695e',
        'user-language': 'zh_CN'
    }
    
    response = requests.post(url, params=params, headers=headers, data=payload, verify=False)
    response.raise_for_status()
    
    result = response.json()
    return result


if __name__ == '__main__':
    import time
    
    for i in range(10000):
        try:
            # gift_id = randrange(211001, 211010)
            # print(gift_id)
            print(f"\n开始第 {i+1} 次送礼...")
            result = pay_room(
                to_uid=[200251443],
                gift_num=1,
                gift_id=211736,
                price=2234180,
                uid=200253866,
                rid=100104312
            )
            print(f"第 {i+1} 次送礼成功")
            
            # 添加延迟，避免请求过快
            time.sleep(25)
            
        except Exception as e:
            print(f"第 {i+1} 次送礼失败: {e}")
            traceback.print_exc()
            break  # 出错时停止，避免无限报错
