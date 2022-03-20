import json
import os

import requests
from bs4 import BeautifulSoup

from pprint import pprint

def create_nick_list(filename):
    nick_list = []
    with open(filename, 'r', encoding='utf-8') as heroes_txt:
        for line in heroes_txt:
            if len(line) > 0:
                line = line.replace(' ', '').replace('\n', '')
                cHeroId, nick = line.split(sep=':', maxsplit=1)
                # print('{} {}'.format(cHeroId, nick))
                nicks = nick.split(',')
                nicks = [word.capitalize() for word in nicks]
                hero_nick = dict(cHeroId=cHeroId, nick=nicks)
                nick_list.append(hero_nick)
    return nick_list


def create_tier_dict():
    tier_dict = {
        1: 'S',
        2: 'A',
        3: 'B',
        4: 'C',
        5: 'D',
    }
    # Герои, записанные иначе
    bug_names = {
        'Deckard Cain': 'Deckard',
        'Lúcio': 'Lucio'
    }

    response = requests.get('https://www.icy-veins.com/heroes/heroes-of-the-storm-general-tier-list')

    soup = BeautifulSoup(response.text, 'html.parser')
    tiers_table_html = soup.find_all('div', attrs={'class': 'htl'})
    count = 1
    tier_hero_list = []
    for hero_tier in tiers_table_html:
        hero_list = hero_tier.find_all('span', attrs={'class': 'hp_50x50'})  # htl_ban_true
        for heroes in hero_list:
            next_element = heroes.find_next_sibling("span")
            name = bug_names.setdefault(next_element.text, next_element.text)
            if name == '': #Доп элемент для вариана из-за span с иконкой роли
                next_element = next_element.find_next_sibling("span")
                name = bug_names.setdefault(next_element.text, next_element.text)
            tier_hero_list.append([name, tier_dict[count]])
        count += 1
    tier_hero_dict = dict(tier_hero_list)
    return tier_hero_dict


if __name__ == '__main__':
    create_heroes_ru_data()
