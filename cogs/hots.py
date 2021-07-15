import json
import os
import sys
import yaml

from discord import Embed
from discord.ext import commands

from hots.function import add_thumbnail, cleanhtml, per_lvl, find_heroes
from hots.heroes import builds, hero_not_found, find_more_heroes, heroes_description_short, args_not_found
from hots.talents import talents, wrong_talent_lvl, read_talent_lvl
from hots.patchnotes import last_pn

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata.json'
heroes_ru_json_file = 'data/heroesdata_ru.json'


class hots(commands.Cog, name="hots"):

    def __init__(self, bot):
        self.bot = bot

    guild_ids = [845658540341592096]  # Put your server ID in this array.

    @commands.command(name="patchnotes")
    async def hots_notes(self, context):
        """
        - Информация по патчноутам
        """
        embed = last_pn(None, context.author)
        await context.send(embed=embed)

    @commands.command(name="hero")
    async def hots_hero(self, context, *args):
        """
        :hero: - Описание героя, билды, разборы
        """
        hero = None
        if len(args) == 0:
            embed = args_not_found('hero')
        else:
            hero_name = ' '.join(map(str, args))  # для имен из нескольких слов
            hero_list = find_heroes(hero_name)
            if len(hero_list) == 1:
                embed = None
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = find_more_heroes(hero_list, context.author)
            else:
                embed = hero_not_found(context.author)
            if hero is not None:
                embed = heroes_description_short(hero, context.author)
                embed = builds(hero, context.author, embed)
                embed = add_thumbnail(hero, embed)
        await context.send(embed=embed)

    @commands.command(name="skill")
    async def hots_skill(self, context, *args):
        """
        :hero: - Скиллы героя
        """
        if len(args) == 0:
            embed = args_not_found('skill')
        else:
            hero = None
            hero_list = find_heroes(args[0])
            if len(hero_list) == 1:
                hero = hero_list[0]
            elif len(hero_list) == 0:
                embed = hero_not_found(context.author)
            elif len(hero_list) > 1:
                embed = find_more_heroes(hero_list, context.author, 'skill')
            if hero is not None:
                # json с данными по всем героям
                with open(heroes_json_file) as heroes_json:
                    heroes_data = json.load(heroes_json)
                # json с внутриигровыми строками перевода текста
                with open(gamestrings_json_file, encoding='utf-8') as ru_json:
                    ru_data = json.load(ru_json)
                # json по отдельному герою, содержит более детальную информацию
                hero_json_file = 'hero/' + hero['name_json']
                with open(hero_json_file) as hero_json:
                    hero_data = json.load(hero_json)
                full_hero = heroes_data[hero_data['cHeroId']]
                basic_ability = full_hero['abilities']['basic']
                trait_ability = full_hero['abilities']['trait']
                # print(trait_ability)
                heroic_ability = full_hero['abilities']['heroic']
                ability = basic_ability + trait_ability + heroic_ability
                embed = Embed(
                    title="Способности героя {}:".format(hero['name_ru']),
                    color=config["success"]
                )
                for i in range(len(ability)):  # считываем все абилки
                    # считываем файл с переводом
                    ability_name = hero_data['abilities'][hero_data['hyperlinkId']][i]['name']
                    ability_nameID = ability[i]['nameId']
                    ability_buttonID = ability[i]['buttonId']
                    ability_hotkey = ability[i]['abilityType']
                    if len(args) > 1:  # если есть аргумент с кнопками
                        abil_keys = args[1].upper()
                        good_key = {'Й': 'Q', 'Ц': 'W', 'У': 'E', 'В': 'D', 'К': 'R'}
                        keys = []
                        for abil_key in abil_keys:
                            if abil_key in good_key.keys():
                                abil_key = good_key.get(abil_key)
                            if abil_key not in good_key.values():
                                embed = Embed(
                                    title="Ошибка выбора клавиши".format(),
                                    color=config["error"]
                                )
                                embed.add_field(
                                    name='После имени введите клавиши нужных способности (можно на русском)',
                                    value="Например: #skill самуро qwe|йцу",
                                    inline=False
                                )
                            abil_key = 'Trait' if abil_key == 'D' else abil_key
                            abil_key = 'Heroic' if abil_key == 'R' else abil_key
                            keys.append(abil_key)
                        if ability_hotkey not in keys:
                            continue
                    try:
                        full_talent_name_en = ability_nameID + '|' + \
                                              ability_buttonID + '|' + ability_hotkey + '|False'
                        ability_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
                    except:
                        full_talent_name_en = ability_nameID + '|' + \
                                              ability_buttonID + '|' + ability_hotkey + '|True'
                        ability_name_ru = ru_data['gamestrings']['abiltalent']['name'][full_talent_name_en]
                    ability_desc_ru = cleanhtml(ru_data['gamestrings']['abiltalent']['full'][full_talent_name_en])
                    try:  # может не быть кулдауна
                        # ability_desc = hero_data['abilities'][hero_data['cHeroId']][i]['description']
                        ability_cooldown = cleanhtml(
                            ru_data['gamestrings']['abiltalent']['cooldown'][full_talent_name_en])
                        cooldown_title, cooldown_time = ability_cooldown.split(':', 1)
                        embed.add_field(
                            name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                            value="{}: _{}_\n{}".format(cooldown_title, cooldown_time, ability_desc_ru),
                            inline=False
                        )
                    except:
                        print(ability[i])
                        embed.add_field(
                            name='{} / {} ({})'.format(ability_name, ability_name_ru, ability_hotkey),
                            value="{}".format(ability_desc_ru),
                            inline=False
                        )
                embed.set_footer(
                    text=f"Текущий патч: {config['patch']}"
                )
            else:
                embed = hero_not_found(context.author)
        await context.send(embed=embed)

    @commands.command(name="talent")
    async def hots_talent(self, context, *args):
        """
        :hero: :lvl: - Таланты героя :lvl: уровня
        """
        if len(args) < 2:
            embed = args_not_found('talent', ':lvl:')
        else:
            hero = None
            hero_name, lvl = read_talent_lvl(args)
            hero_list = find_heroes(hero_name)
            if len(hero_list) == 1:
                embed = None
                hero = hero_list[0]
            elif len(hero_list) > 1:
                embed = find_more_heroes(hero_list, context.author, 'talent', ':lvl:')
            else:
                embed = hero_not_found(context.author)
            if hero is not None:
                try:
                    embed = talents(hero, lvl, context.author)
                except:
                    embed = wrong_talent_lvl(context.author)
        await context.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(hots(bot))
