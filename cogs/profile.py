import os
import sys

from discord import Embed, utils
import yaml
import random
from discord.ext import commands
from helpers import sql
import requests
from bs4 import BeautifulSoup
from hots.Player import Player

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


def get_heroesprofile_data(btag, discord_name):
    bname = btag.replace('#', '%23')
    base_url = 'https://www.heroesprofile.com'
    url = 'https://www.heroesprofile.com/Search/?searched_battletag=' + bname
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    response = requests.get(url, headers={"User-Agent": f"{user_agent}"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    error = soup.find('div', attrs={'id': 'choose_battletag'})
    if error is not None:
        links = error.find_all('a')
        for link in links:
            region = 'ion=2'
            if region in link['href']:
                url_new = base_url + link['href'].replace('®', '&reg')
        print(url_new)
        response = requests.get(url_new, headers={"User-Agent": f"{user_agent}"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

    mmr_container = soup.find('section', attrs={'class': 'mmr-container'})
    mmr_info = mmr_container.find_all('div', attrs={'class': 'league-element'})
    for elem in mmr_info:
        if elem.h3.text == 'Storm League':
            tags = elem.find_all('div')
            for tag in tags[:1]:
                profile_data = (" ".join(tag.text.split())).split()
                profile_wr = profile_data[2]
                if profile_data[3] == 'Master':
                    profile_league = profile_data[3]
                    profile_mmr = profile_data[5]
                else:
                    profile_league = profile_data[3] + profile_data[4]
                    profile_mmr = profile_data[6]
                return Player(btag, discord_name, profile_mmr, profile_league, profile_wr)
    return None


def get_player(record):
    if record is not None:
        player = Player(btag=record[0], discord=record[4], mmr=record[3], league=record[1], winrate=record[2])
        return player
    return None


def get_profile_embed(player: Player):
    embed = Embed(
        title=f"Профиль игрока {player.btag}",
        color=config["info"]

    )
    embed.add_field(
        name="Лига",
        value=player.league,
        inline=True
    )
    embed.add_field(
        name="ММР",
        value=player.mmr,
        inline=True
    )
    return embed


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
    async def profile_add(self, ctx, btag, discord_user):
        print("profile_add")
        data = None
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor()
        select = """SELECT * FROM heroesprofile WHERE btag = %s"""
        cur.execute(select, (btag,))
        record = cur.fetchone()
        print(record)
        if record is not None and record[4] is None:
            cur.execute("""UPDATE heroesprofile SET discord=%s WHERE btag=%s""", (discord_user, btag))
            con.commit()
            await ctx.send(f"В запись пользователя {btag} добавлен дискорд профиль")
            con.close()
        if record is None:
            try:
                data = get_heroesprofile_data(btag, discord_user)
                insert = """INSERT INTO heroesprofile(BTAG, RANK, WINRATE, MMR, DISCORD) 
                            VALUES(%s, %s, %s, %s, %s )"""
                cur.execute(insert, (data.btag, data.league, data.winrate, data.mmr, data.discord))
                con.commit()
                con.close()
                await ctx.send(f"Профиль игрока {btag} добавлен в базу")
            except:
                await ctx.send(f'Профиль игрока {btag} не найден')

    @profile.command(name="update")
    async def profile_update(self, ctx, user_or_btag):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor()
        select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(select, (user_or_btag, user_or_btag,))
        record = cur.fetchone()
        print(record)
        player = get_player(record)
        if player is not None:
            try:
                data = get_heroesprofile_data(player.btag, player.discord)
                update = """UPDATE heroesprofile SET RANK=%s, WINRATE=%s, MMR=%s WHERE btag=%s"""
                cur.execute(update, (data.league, data.winrate, data.mmr, data.btag))
                con.commit()
                con.close()
                await ctx.send(f"Профиль игрока {player.btag} обновлен")
            except:
                await ctx.send(f'Профиль игрока {player.btag} не найден')
        else:
            await ctx.send(f'Профиль игрока {user_or_btag} не найден')

    @profile.command(name="info")
    async def profile_info(self, ctx, user_or_btag):
        sql.sql_init()
        con = sql.get_connect()
        cur = con.cursor()
        select = """SELECT * FROM heroesprofile WHERE discord = %s OR btag = %s"""
        cur.execute(select, (user_or_btag, user_or_btag,))
        record = cur.fetchone()
        print(record)
        if record is not None:
            player = Player(btag=record[0], discord=record[4], mmr=record[3], league=record[1], winrate=record[2])
            embed = get_profile_embed(player)
            await ctx.send(embed=embed)

    @profile.error
    @profile_add.error
    async def profile_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Не хватает аргументов. Необходимо указать батлтег и дискорд профиль")


def setup(bot):
    bot.add_cog(Profile(bot))
