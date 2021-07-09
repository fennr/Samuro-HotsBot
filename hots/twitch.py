import os
import sys
import yaml

from twitchAPI.twitch import Twitch
from discord import Embed

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

def get_streams(first = 6):
    twitch_app_key = 'podhxqero17w9mlhuxr67xt13dw10i'
    twitch_sec_token = '16lwbqc8b42eh67aq2m3c2lxnxkuy0'
    twitch = Twitch(twitch_app_key, twitch_sec_token)
    twitch.authenticate_app([])

    hots_id = ['32959']
    language = ['ru']
    url = 'https://www.twitch.tv/'
    response_channels = twitch.get_streams(game_id=hots_id, language=language)
    count = 0
    embed = Embed(
        title='Стримы онлайн',
        color=config["success"]
    )
    for stream in response_channels['data']:
        if count < first:
            link = '[' + stream['title'] + '](' + url + stream['user_login'] + ')'
            embed.add_field(
                name=f"{stream['user_name']}",
                value=f"{link}\nЗрителей: {stream['viewer_count']}",
                inline=False
            )
            count += 1
    return embed

