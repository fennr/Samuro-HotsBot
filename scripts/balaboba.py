# -*- coding: utf-8 -*-
from requests import post

def balaboba(str):
    url = 'https://yandex.ru/lab/api/yalm/text3'
    data = {"query": text, "intro": 0, "filter": 1}
    resp = post(url, json=data).json()
    print(resp)
    return(resp['query'] + resp['text'])

text = 'Кому на руси жить хорошо'
generate = balaboba(text)

print(generate)