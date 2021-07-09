import os
import sys
import yaml
import json
from discord import Embed
from discord.ext.commands import command, Cog
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

from hots.function import open_hero, find_heroes
from hots.heroes import heroes_description, builds
from hots.skills import skill, skills
from hots.talents import talents
from hots.patchnotes import last_pn
from hots.nexuscompendium import weekly_rotation
from hots.twitch import get_streams

# Only if you want to use variables that are in the config.yaml file.
if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

short_patch = config["patch"][-5:]

gamestrings_json_file = 'data/gamestrings' + short_patch + '.json'
heroes_json_file = 'data/heroesdata.json'

with open(heroes_json_file) as heroes_json:
    heroes_data = json.load(heroes_json)
with open(gamestrings_json_file, encoding='utf-8') as ru_json:
    ru_data = json.load(ru_json)

# menu
heroes_label = 'Герой'
skills_label = 'Скиллы'
talent_label = 'Таланты'
lastpn_label = 'Патч'

# hero
descrp_label = 'Описание'
patchn_label = 'Патчноуты'
builds_label = 'Билды'

# skills
basic_label = 'Базовые'
heroic_label = "Героические"
trait_label = 'Особые'

# talents
lvl_01_label = '1'
lvl_04_label = '4'
lvl_07_label = '7'
lvl_10_label = '10'
lvl_13_label = '13'
lvl_16_label = '16'
lvl_20_label = '20'


class Heroes(Cog, name='heroes'):
    def __init__(self, bot):
        self.bot = bot


    @command(name='rotate')
    async def rotation(self, ctx):
        """
        Список героев еженедельной ротации
        """
        embed = weekly_rotation()
        await ctx.send(
            embed=embed
        )


    @command(name='data')
    async def data(self, ctx, *args):
        """
        Единый интерфейс описания героя
        Указать имя героя
        -----
        """
        global hero
        if len(args) == 0:
            embed = Embed(
                title="После команды введите имя героя на русском или английском",
                color=config["error"]
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config['bot_prefix']}hero2 Самуро",
                inline=False
            )
        else:
            hero_list = find_heroes(args[0])
            if len(hero_list) == 1:
                hero = hero_list[0]
            elif len(hero_list) == 0:
                embed = Embed(
                    title="Ошибка! Герой не найден",
                    color=config["error"]
                )
            elif len(hero_list) > 1:
                hero = None
                embed = Embed(
                    title="Возможно вы имели в виду:",
                    color=config["warning"]
                )
                for wrong_hero in hero_list:
                    embed.add_field(
                        name="{} / {}".format(wrong_hero['name_en'], wrong_hero['name_ru']),
                        value=f"Введи: {config['bot_prefix']}hero {wrong_hero['name_ru']}",
                        inline=False
                    )
                embed.set_footer(
                    text=f"Информация для: {ctx.author}"
                    # text=f"Текущий патч: {config['patch']}"
                )
            if hero is not None:
                embed = builds(hero, ctx.author)
                default_hero_name = hero['name_en'].lower().replace('.', '').replace("'", "")
                heroespn_url = 'https://heroespatchnotes.com/hero/'
                heroespn_url_full = heroespn_url + default_hero_name.replace(' ', '') + '.html'
                menu_buttons = [
                    Button(style=ButtonStyle.blue, label=heroes_label, disabled=True),
                    Button(style=ButtonStyle.blue, label=skills_label),
                    Button(style=ButtonStyle.blue, label=talent_label),
                    Button(style=ButtonStyle.blue, label=lastpn_label),
                ]
                hero_buttons = [
                    Button(style=ButtonStyle.grey, label=descrp_label),
                    Button(style=ButtonStyle.grey, label=builds_label, disabled=True),
                    Button(style=ButtonStyle.URL, label=patchn_label, url=heroespn_url_full),
                ]
                await ctx.send(
                    embed=embed,
                    components=[
                        hero_buttons,
                        menu_buttons
                    ],
                )


    @command(name='streams')
    async def streams(self, ctx, *args):
        """
        Онлайн стримы на твиче
        Указать количество
        -----
        """
        if len(args) == 1 and args[0].isdigit():
            embed = get_streams(int(args[0]))
        else:
            embed = get_streams()
        await ctx.send(
            embed=embed
        )

    @Cog.listener()
    async def on_button_click(self, res):
        """
        Possible interaction types:
        - Pong
        - ChannelMessageWithSource
        - DeferredChannelMessageWithSource
        - DeferredUpdateMessage
        - UpdateMessage
        """
        hero_name, tail = res.raw_data['d']['message']['embeds'][0]['title'].split(' / ', maxsplit=1)
        text, author = res.raw_data['d']['message']['embeds'][-1]['footer']['text'].split(': ', maxsplit=1)
        hero = open_hero(hero_name)

        default_hero_name = hero_name.lower().replace('.', '').replace("'", "")
        heroespn_url = 'https://heroespatchnotes.com/hero/'
        heroespn_url_full = heroespn_url + default_hero_name.replace(' ', '') + '.html'

        menu_buttons = [
            Button(style=ButtonStyle.blue, label=heroes_label),
            Button(style=ButtonStyle.blue, label=skills_label),
            Button(style=ButtonStyle.blue, label=talent_label),
            Button(style=ButtonStyle.blue, label=lastpn_label),
        ]
        hero_buttons = [
            Button(style=ButtonStyle.grey, label=descrp_label),
            Button(style=ButtonStyle.grey, label=builds_label),
            Button(style=ButtonStyle.URL, label=patchn_label, url=heroespn_url_full),
        ]
        skill_buttons = [
            Button(style=ButtonStyle.grey, label=basic_label),
            Button(style=ButtonStyle.grey, label=heroic_label),
            Button(style=ButtonStyle.grey, label=trait_label),
        ]
        talent_buttons1 = [
            Button(style=ButtonStyle.grey, label=lvl_01_label),
            Button(style=ButtonStyle.grey, label=lvl_04_label),
            Button(style=ButtonStyle.grey, label=lvl_07_label),
            Button(style=ButtonStyle.grey, label=lvl_10_label),
        ]
        talent_buttons2 = [
            Button(style=ButtonStyle.grey, label=lvl_13_label),
            Button(style=ButtonStyle.grey, label=lvl_16_label),
            Button(style=ButtonStyle.grey, label=lvl_20_label),
        ]

        skill_components = [
            skill_buttons,
            menu_buttons
        ]
        hero_components = [
            hero_buttons,
            menu_buttons
        ]
        talent_components = [
            talent_buttons1,
            talent_buttons2,
            menu_buttons
        ]
        lastpn_components = [
            menu_buttons
        ]

        if res.component.label == descrp_label or \
                res.component.label == heroes_label:
            embed = heroes_description(hero, author)
            components = hero_components
            components[0][0] = Button(style=ButtonStyle.grey, label=descrp_label, disabled=True)
            components[1][0] = Button(style=ButtonStyle.blue, label=heroes_label, disabled=True)
        if res.component.label == builds_label:
            embed = builds(hero, author)
            components = hero_components
            components[0][1] = Button(style=ButtonStyle.grey, label=builds_label, disabled=True)
            components[1][0] = Button(style=ButtonStyle.blue, label=heroes_label, disabled=True)

        if res.component.label == skills_label:
            embed = skill(hero, author)
            components = skill_components
            components[0][0] = Button(style=ButtonStyle.grey, label=basic_label, disabled=True)
            components[1][1] = Button(style=ButtonStyle.blue, label=skills_label, disabled=True)
        if res.component.label == basic_label:
            embed = skills(hero, 'basic', author)
            components = skill_components
            components[0][0] = Button(style=ButtonStyle.grey, label=basic_label, disabled=True)
            components[1][1] = Button(style=ButtonStyle.blue, label=skills_label, disabled=True)
        if res.component.label == heroic_label:
            embed = skills(hero, 'heroic', author)
            components = skill_components
            components[0][1] = Button(style=ButtonStyle.grey, label=heroic_label, disabled=True)
            components[1][1] = Button(style=ButtonStyle.blue, label=skills_label, disabled=True)
        if res.component.label == trait_label:
            embed = skills(hero, 'trait', author)
            components = skill_components
            components[0][2] = Button(style=ButtonStyle.grey, label=trait_label, disabled=True)
            components[1][1] = Button(style=ButtonStyle.blue, label=skills_label, disabled=True)

        if res.component.label == talent_label or \
                res.component.label == lvl_01_label:
            embed = talents(hero, 1, author)
            components = talent_components
            components[0][0] = Button(style=ButtonStyle.grey, label=lvl_01_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lvl_04_label:
            embed = talents(hero, 4, author)
            components = talent_components
            components[0][1] = Button(style=ButtonStyle.grey, label=lvl_04_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lvl_07_label:
            embed = talents(hero, 7, author)
            components = talent_components
            components[0][2] = Button(style=ButtonStyle.grey, label=lvl_07_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lvl_10_label:
            embed = talents(hero, 10, author)
            components = talent_components
            components[0][3] = Button(style=ButtonStyle.grey, label=lvl_10_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lvl_13_label:
            embed = talents(hero, 13, author)
            components = talent_components
            components[1][0] = Button(style=ButtonStyle.grey, label=lvl_13_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lvl_16_label:
            embed = talents(hero, 16, author)
            components = talent_components
            components[1][1] = Button(style=ButtonStyle.grey, label=lvl_16_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lvl_20_label:
            embed = talents(hero, 20, author)
            components = talent_components
            components[1][2] = Button(style=ButtonStyle.grey, label=lvl_20_label, disabled=True)
            components[2][2] = Button(style=ButtonStyle.blue, label=talent_label, disabled=True)
        if res.component.label == lastpn_label:
            embed = last_pn(hero, author)
            components = lastpn_components
            components[0][3] = Button(style=ButtonStyle.blue, label=lastpn_label, disabled=True)
        if author == str(res.user):
            await res.respond(
                type=InteractionType.UpdateMessage, embed=embed, components=components
            )
        else:
            error_text = 'Команда вызвана другим пользователем, взаимодействие невозможно\n' \
                         'Вызовите команду для получения информации по герою'
            await res.respond(
                type=InteractionType.ChannelMessageWithSource, content=f"{error_text}"
            )
            # можно использовать или embed или content content=f"{res.component.label} pressed",


def setup(bot):
    DiscordComponents(bot)  # If you have this in an on_ready() event you can remove this line.
    bot.add_cog(Heroes(bot))
