import os
import sys

from discord import Embed, utils
import yaml
import random
from discord.ext import commands
from helpers import sql
import requests
from bs4 import BeautifulSoup

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class Profile(commands.Cog, name="profile"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="profile")
    async def profile(self, ctx):
        """
        - Информация по Батлтегу
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Для добавления игрока используйте команду #profile add батлтег дискорд\n '
                           'Пример: #profile add player#1234 @player')

    @profile.command(name="test")
    async def profile_test(self, ctx, *args):
        if len(args) > 1:
            btag = args[0]
            user = args[1]
        await ctx.send(f"Пользователь {user} добавлен")

    @profile.command(name="add")
    async def profile_add(self, ctx, btag, user):
        data = None
        if btag is None or user is None:
            await ctx.send(f"Введите батлтег и дискордтег после add")
        else:
            sql.sql_init()
            con = sql.get_connect()
            cur = con.cursor()
            select = """SELECT * FROM heroesprofile WHERE btag = %s"""
            cur.execute(select, (btag,))
            record = cur.fetchone()
            if record is not None and record[4] is None:
                cur.execute("""UPDATE heroesprofile SET discord=%s WHERE btag=%s""", (user, btag))
                con.commit()
                await ctx.send(f"В запись пользователя {btag} добавлен дискорд профиль")
                con.close()
            if record is None:
                try:
                    bname = btag
                    btag = btag.replace('#', '%23')
                    base_url = 'https://www.heroesprofile.com'
                    url = 'https://www.heroesprofile.com/Search/?searched_battletag=' + btag
                    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
                    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    error = soup.find('div', attrs={'id': 'choose_battletag'})
                    if error is not None:
                        links = error.find_all('a')
                        for link in links:
                            url_new = base_url + link['href'].replace('®', '&reg')
                        response = requests.get(url_new, headers={"User-Agent": f"{user_agent}"})
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')

                    mmr_container = soup.find('section', attrs={'class': 'mmr-container'})
                    mmr_info = mmr_container.find_all('div', attrs={'class': 'league-element'})
                    flag = False
                    for elem in mmr_info:
                        if elem.h3.text == 'Storm League':
                            flag = True
                            tags = elem.find_all('div')
                            for tag in tags[:1]:
                                profile_data = (" ".join(tag.text.split())).split()
                                # print(profile_data)
                                profile_wr = profile_data[2]
                                if profile_data[3] == 'Master':
                                    profile_league = profile_data[3]
                                    profile_mmr = profile_data[5]
                                else:
                                    profile_league = profile_data[3] + profile_data[4]
                                    profile_mmr = profile_data[6]
                                print(f"Игрок: {bname}")
                                print(f"Винрейт: {profile_wr}")
                                print(f"Лига: {profile_league}")
                                print(f"ММР: {profile_mmr}")
                                data = {'btag': bname,
                                        'rank': profile_league,
                                        'winrate': profile_wr,
                                        'mmr': profile_mmr,
                                        'discord': user
                                        }
                                cur.execute("""INSERT INTO heroesprofile(BTAG, RANK, WINRATE, MMR, DISCORD) 
                                                        VALUES(%(btag)s, %(rank)s, %(winrate)s, %(mmr)s, %(discord)s )""",
                                            data)
                                con.commit()
                                con.close()
                                await ctx.send(f"Профиль игрока {btag} добавлен в базу")
                except:
                    await ctx.send(f'Профиль игрока {bname} не найден')

    @profile.command(name="info")
    async def profile_info(self, ctx, user):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor()
        select = """SELECT * FROM heroesprofile WHERE discord = %s"""
        cur.execute(select, (user,))
        record = cur.fetchone()
        if record is not None:
            data = {'btag': record[0],
                    'rank': record[1],
                    'winrate': record[2],
                    'mmr': record[3],
                    'discord': record[4]
                    }
            embed = Embed(
                title=f"Профиль игрока {data['btag']}",
                color=config["info"]

            )
            embed.add_field(
                name="Лига",
                value=data['rank'],
                inline=True
            )
            embed.add_field(
                name="Винрейт",
                value=data['winrate'],
                inline=True
            )
            embed.add_field(
                name="ММР",
                value=data['mmr'],
                inline=True
            )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Profile(bot))
