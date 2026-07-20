#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Google 翻译 API 封装。"""
import json
from dataclasses import asdict, dataclass

import requests
from requests.adapters import HTTPAdapter, Retry

# API URL：直接在此填写完整的 Google 翻译 API 地址（含 Key）
_API_URL = 'https://translation.googleapis.com/language/translate/v2?key=AIzaSyDtDQGXVQgO2WSp9EAsFvZYIxrVxxtuNZg'

_HEADERS = {'Content-Type': 'application/json'}

# 重试配置
_RETRY_CONFIG = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503]
)


class TranslationError(Exception):
    """翻译错误"""


@dataclass
class TranslationModel:
    """翻译数据模型。"""
    language: str = 'en'
    text: str = ''

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class GoogleTranslator:
    """Google 翻译器（带请求重试）。"""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=_RETRY_CONFIG))
        self.session.mount('http://', HTTPAdapter(max_retries=_RETRY_CONFIG))

    def translate(self, text: str, target_lang: str) -> str:
        """翻译文本。"""
        if not text:
            return text
        
        payload = {"target": target_lang, "q": text}

        try:
            resp = self.session.post(
                _API_URL,
                data=json.dumps(payload),
                headers=_HEADERS,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()

            translations = result.get('data', {}).get('translations', [])
            if translations:
                return translations[0].get('translatedText', text)

            return text

        except requests.RequestException as e:
            raise TranslationError(f"Translation request failed: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise TranslationError(f"Invalid response format: {e}")