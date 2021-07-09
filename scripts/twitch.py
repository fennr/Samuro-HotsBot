from twitchAPI.twitch import Twitch
from pprint import pprint

# create instance of twitch API
twitch = Twitch('podhxqero17w9mlhuxr67xt13dw10i', '16lwbqc8b42eh67aq2m3c2lxnxkuy0')
twitch.authenticate_app([])

# get ID of user
user_info = twitch.get_users(logins=['mr_fennr'])
user_id = user_info['data'][0]['id']
#pprint(twitch.get_users(logins=['mr_fennr']))

'''hots_channels = twitch.search_channels('Heroes of the Storm', first=100)
url = 'https://www.twitch.tv/'

for stream in hots_channels['data']:
    data = twitch.get_channel_information(stream['id'])
    if stream['broadcaster_language'] == 'ru':
        print("streamer: {}\nname: {}\nurl: {}".format(stream['display_name'], stream['title'], url+stream['broadcaster_login']))
        pprint(data)'''

hots_id = ['32959']
language = ['ru']
url = 'https://www.twitch.tv/'
response_channels = twitch.get_streams(game_id=hots_id, language=language)
for stream in response_channels['data']:
    print("streamer: {}\nname: {}\nurl: {}".format(stream['user_name'], stream['title'], url+stream['user_login']))
