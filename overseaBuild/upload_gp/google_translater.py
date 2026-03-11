import requests
import json
import base64

url = 'aHRfkfkHkdndJlNjdjHkGUvdjI/a2V5PUFJemFTeUR0RFFHWFZRZ08yV1NwOUVBc0Z2WllJeHJWeHh0dU5aZw=='
headers = {
    'Content-Type': 'application/json'
}


class GoogleTranslater:
    def translate(self, text, targetLan):
        values = {"target": targetLan, "q": text}
        response = requests.post(base64.b64decode(url), data=json.dumps(values), headers=headers)

        res = json.loads(response.text)
        if res['data'] and res['data']['translations']:
            translations = res['data']['translations']
            if len(translations) > 0:  # 检验文本长度
                return translations[0]['translatedText']
        return text


class JsonCustomEncoder(json.JSONEncoder):
    def default(self, field):
        if isinstance(field, Model):
            return field.toMap()
        else:
            return json.JSONEncoder.default(self, field)  # ds = json.dumps(d, cls=JsonCustomEncoder)


class Model:
    language = 'en'
    text = ''

    def toMap(self):
        return {'language': self.language, 'text': self.text}
