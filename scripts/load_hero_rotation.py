import json
import requests

url = 'https://nexuscompendium.com/api/currently/herorotation'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
response = requests.get(url, headers={f"User-Agent":"{user_agent}"})
data = response.json()
start_date = data['RotationHero']['StartDate']
end_date = data['RotationHero']['EndDate']
heroes = data['RotationHero']['Heroes']
hero_list = []
for hero in heroes:
	hero_list.append(hero['Name'])

print('Начало: {}'.format(start_date))
print('Конец: {}'.format(end_date))
print(hero_list)