import os
import sys
import requests
import yaml
import psycopg2.extras
import itertools as it
import pytz
import exceptions
from datetime import datetime
from discord import Embed, utils, Member
from discord.ext import commands
from helpers import sql, check
from bs4 import BeautifulSoup
from hots.Player import Player
from statistics import mean

if __name__ == '__main__':
    sql.sql_init()
    con = sql.get_connect()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    select = """SELECT * FROM heroesprofile"""
    cur.execute(select)
    rec = cur.fetchall()
    for player_list in rec:
        player = Player(btag=player_list['btag'], league=player_list['rank'], division='',
                        discord=player_list['discord'],
                        mmr=player_list['mmr'], win=player_list['win'],
                        lose=player_list['lose'], winrate=player_list['winrate'])
        mmr_old = player.mmr
        player.mmr = player.mmr + (int(player.win) * 20) - (int(player.lose) * 20)
        update = '''UPDATE heroesprofile SET mmr = %s WHERE btag=%s'''
        cur.execute(update, (player.mmr, player.btag))
    print(f"{player.btag} {mmr_old} -> {player.mmr}")
    con.commit()
    con.close()
