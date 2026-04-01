#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 翻译 API 封装
"""
import base64
import json
from typing import Any

import requests

# API URL (Base64 编码)
_API_URL = base64.b64decode(
    'aHR0cHM6Ly90cmFuc2xhdGUuZ29vZ2xlYXBpcy5jb20vdHJhbnNsYXRlL2EyL2tleT1BSXphU3lEdERRR1hWUWdPMldTcDlFQXNGdlpZSXhyVnh4dHVOWmc='
).decode('utf-8')

_HEADERS = {'Content-Type': 'application/json'}


class TranslationError(Exception):
    """翻译错误"""
    pass


class GoogleTranslator:
    """Google 翻译器"""

    def translate(self, text: str, target_lang: str) -> str:
        """翻译文本
        
        :param text: 要翻译的文本
        :param target_lang: 目标语言代码
        :return: 翻译后的文本
        :raises TranslationError: 翻译失败时抛出
        """
        if not text:
            return text
        
        payload = {"target": target_lang, "q": text}
        
        try:
            resp = requests.post(
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


class ModelEncoder(json.JSONEncoder):
    """自定义 JSON 编码器"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, TranslationModel):
            return obj.to_dict()
        return super().default(obj)


class TranslationModel:
    """翻译数据模型"""
    
    def __init__(self, language: str = 'en', text: str = ''):
        self.language = language
        self.text = text
    
    def to_dict(self) -> dict[str, str]:
        return {'language': self.language, 'text': self.text}
