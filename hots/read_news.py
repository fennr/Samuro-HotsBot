import json
import os
import sys
from typing import List

import yaml
from discord import Embed

import base64
from github import Github
from pprint import pprint

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]


def print_repo(repo):
    # repository full name
    print("Full name:", repo.full_name)
    # repository description
    print("Description:", repo.description)
    # the date of when the repo was created
    print("Date created:", repo.created_at)
    # the date of the last git push
    print("Date of last push:", repo.pushed_at)
    # home website (if available)
    print("Home Page:", repo.homepage)
    # programming language
    print("Language:", repo.language)
    # number of forks
    print("Number of forks:", repo.forks)
    # number of stars
    print("Number of stars:", repo.stargazers_count)
    print("-" * 50)
    # repository content (files & directories)
    print("Contents:")
    for content in repo.get_contents(""):
        print(content)
    try:
        # repo license
        print("License:", base64.b64decode(repo.get_license().content.encode()).decode())
    except:
        pass


def read_news(file_path='data/news.md') -> List:
    if 'github_token' in os.environ:
        token = os.environ.get('github_token')
    else:
        print('Тестовый ключ Github')
        token = str(config["github_test"])
    g = Github(token)
    repo_name = 'fennr/discord-bot'
    repo = g.get_repo(repo_name)
    file = repo.get_contents(file_path, ref="master")
    data = file.decoded_content.decode("utf-8")
    if len(data) == 0:
        return []
    news_raw_list = data.split('---')
    news_list = []
    for news in news_raw_list:
        head = ''
        date = ''
        desc = ''
        link = ''
        lines: List[str] = news.split('\n')
        for line in lines:
            if line != '':
                if line[0:2] == '##':
                    head = line[2:]
                elif line[0:2] == '__':
                    date = line[2:-2]
                elif line[0:10] == '[Источник]':
                    link = line + '\n'
                else:
                    desc += '\n' + line + '\n'
        news_list.append(dict(header=head, description=desc, date=date, url=link))
    pprint(news_list)
    return news_list


def embed_news(author, embed=None) -> Embed:
    news_path = 'data/news.md'
    news_list = read_news(file_path=news_path)
    if not news_list:
        embed = Embed(
            title='Сейчас нет новых новостей',
            color=config["info"]
        )
    else:
        if embed is None:
            embed = Embed(
                title='Новости',
                color=config["info"]
            )
        for news in news_list:
            name = ':pushpin: ' + news["header"]
            value = ''
            if news["date"] != '':
                name += ' (' + news["date"] + ')'
            value += news["description"] + news["url"]
            embed.add_field(
                name=name,
                value=value,
                inline=False
            )
        embed.set_footer(
            # text=f"Информация для: {author}"  # context.message.author если использовать без slash
            text=f"Предложить новость можно командой #news :текст:\n "
                 f"Чтобы добавить рассылку на сервер написать мне: fenrir#5455"
            # text=f"Текущий патч: {config['patch']}"
        )
    return embed
