import json
import re
import requests
from flask_babel import _
from appPackage import appFlask
import appPackage

def translate(text, source_language, dest_language):
    if 'API_YANDEX_KEY' not in appFlask.config or not appFlask.config['API_YANDEX_KEY']:
        return _('Error: the translation service is not configured.')

    API_KEY = appFlask.config['API_YANDEX_KEY']
    folder_id = appFlask.config['API_YANDEX_CATALOG_ID']
    url = appFlask.config['API_YANDEX_URL']
    texts = []
    texts.append(text)
   

    body = {
        "sourceLanguageCode": source_language,
        "targetLanguageCode": dest_language,
        "texts": texts,
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {0}".format(API_KEY)
    }

    response = requests.post(url, json = body, headers = headers)

    if response.status_code != 200:
        return _('Error: the translation service failed.')

    response_json = response.json()
    return response_json['translations'][0]['text']

# {
#  "translations": [ {"text": "Hi, how are you doing?"} ]
# }

def guess_language(text):
    if 'API_YANDEX_KEY' not in appFlask.config or not appFlask.config['API_YANDEX_KEY']:
        return _('Error: the translation service is not configured.')

    API_KEY = appFlask.config['API_YANDEX_KEY']
    DEST_LANGUAGE = 'en'
    folder_id = appFlask.config['API_YANDEX_CATALOG_ID']
    url = appFlask.config['API_YANDEX_URL']
    texts = []
    texts.append(text)
   

    body = {
        "targetLanguageCode": DEST_LANGUAGE,
        "texts": texts,
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {0}".format(API_KEY)
    }

    response = requests.post(url, json = body, headers = headers)

    if response.status_code != 200:
        return _('Error: the translation service failed.')

    response_json = response.json()
    return response_json['translations'][0]['detectedLanguageCode']
