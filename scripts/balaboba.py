import requests

url = 'https://yandex.ru/lab/yalm?style=0'

response = requests.get(url)
print(response.text)
