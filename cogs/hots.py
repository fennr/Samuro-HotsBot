""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""

import inspect
from discord import Embed
from discord.ext import commands
from discord.ext.commands import command, Cog, errors
from discord_components import DiscordComponents, Button, ButtonStyle

from utils.library.hots import hero_not_found, find_more_heroes, get_hero, get_master_opinion, add_master_opinion
from utils.classes.Hero import Hero
from utils.hots.heroes import heroes_description, builds, embed_stlk_builds
from utils.hots import nexuscompendium
from utils.hots.patchnotes import last_pn
from utils.hots.skills import skill
from utils.hots.talents import talents
from utils.hots.tierlist import ban_heroes
from utils.hots.twitch import get_streams
from utils.library import files
from utils import check, exceptions
from utils.classes.Const import config

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


mailing_channel_id = {
    'test_fenrir': 845658540341592098,  # test
    'ru hots': 642853714515722241,      # общение
    'Dungeon': 858455796412710922,      # hots камеры
    'Stlk': 124864790110797824,         # общие
    'Читер': 841669769115336704         # хотс
}

class Hots(Cog, name='Hots'):
    """
    — Команды связанные с хотсом помимо информации о героях
    """
    def __init__(self, bot):
        self.bot = bot

    @command(name='weekly')
    async def rotation(self, ctx):
        """
        - Список героев еженедельной ротации
        """
        embed = nexuscompendium.weekly_rotation()
        await ctx.send(embed=embed)

    @command(name="pancho")
    async def pancho(self, ctx, hero_name):
        """
        - Мнение Мастера
        """
        pancho = get_master_opinion(ctx, hero_name)
        if isinstance(pancho, Embed):
            await ctx.send(embed=pancho)
        else:
            await ctx.send(pancho)

    @command(name="pancho_add")
    @check.is_owner()
    async def pancho_add(self, ctx, hero_name, url):
        error = add_master_opinion(hero_name, url)
        if not error:
            await ctx.send("Запись была добавлена")
        else:
            await ctx.send("Ошибка при записи")

    @command(name="patchnotes")
    async def hots_notes(self, ctx):
        """
        - Информация по патчноутам
        """
        embed = last_pn(None, ctx.author)
        await ctx.send(embed=embed)

    @command(name='ban')
    async def ban_list(self, ctx):
        """
        - Список героев рекомендуемых к бану
        """
        embed = ban_heroes()
        await ctx.send(
            embed=embed
        )

    @command(name='sales')
    async def sales(self, ctx):
        """
        - Список скидок на героев
        """
        embed = nexuscompendium.sales()
        await ctx.send(
            embed=embed
        )

    @command(name='ranked')
    async def ranked(self, ctx):
        """
        - Информация о сроках текущего сезона
        """
        embed = nexuscompendium.ranked()
        await ctx.send(
            embed=embed
        )

    @command(name='data')
    async def heroes_data(self, ctx, hero_name):
        """
        - Полное описания героя
        """
        if hero_name is not None:
            hero = get_hero(hero_name)
            if isinstance(hero, Hero):
                embed = builds(hero, ctx.author)
                default_hero_name = hero.en.lower().replace('.', '').replace("'", "")
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
            else:
                embed = find_more_heroes(hero, ctx.author, command='data')
                await ctx.send(embed=embed)
        else:
            embed = hero_not_found()
            await ctx.send(embed=embed)

    @command(name='streams')
    async def streams(self, ctx, count=5):
        """
        - Ссылки на запущенные стримы на твиче
        """
        if isinstance(int(count), int):
            embed = get_streams(int(count))
        else:
            embed = get_streams()
        await ctx.send(
            embed=embed
        )

    @command(name='stlk')
    async def stlk_builds(self, ctx, *hero_name):
        """
        - Авторские билды от про игрока **STLK**
        """
        if len(hero_name) == 0:
            param = inspect.Parameter(name="hero_name", kind=inspect.Parameter.VAR_POSITIONAL)
            raise commands.MissingRequiredArgument(param)
        name = ' '.join(hero_name)
        hero = get_hero(name)
        if isinstance(hero, Hero):
            embed = embed_stlk_builds(hero, ctx.author, ad=True)
        else:
            embed = find_more_heroes(hero, ctx.author, command="stlk")

        await ctx.send(embed=embed)

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
        embed = None
        components = None
        hero_name, tail = res.raw_data['message']['embeds'][0]['title'].split(' / ', maxsplit=1)
        text, author = res.raw_data['message']['embeds'][-1]['footer']['text'].split(': ', maxsplit=1)
        hero = Hero(hero_name)

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

        if res.component.label == descrp_label:
            embed = heroes_description(hero, author)
            components = hero_components
            components[0][0] = Button(style=ButtonStyle.grey, label=descrp_label, disabled=True)
            components[1][0] = Button(style=ButtonStyle.blue, label=heroes_label, disabled=True)
        if res.component.label == builds_label or \
                res.component.label == heroes_label:
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
            embed = skill(hero, author, 'basic')
            components = skill_components
            components[0][0] = Button(style=ButtonStyle.grey, label=basic_label, disabled=True)
            components[1][1] = Button(style=ButtonStyle.blue, label=skills_label, disabled=True)
        if res.component.label == heroic_label:
            embed = skill(hero, author, 'heroic')
            components = skill_components
            components[0][1] = Button(style=ButtonStyle.grey, label=heroic_label, disabled=True)
            components[1][1] = Button(style=ButtonStyle.blue, label=skills_label, disabled=True)
        if res.component.label == trait_label:
            embed = skill(hero, author, 'trait')
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
                type=7, embed=embed, components=components
            )
        else:
            error_text = 'Команда вызвана другим пользователем, взаимодействие невозможно\n' \
                         'Введите /data :hero: для получения информации по герою'
            await res.respond(
                type=4, content=f"{error_text}"
            )
            # можно использовать или embed или content content=f"{res.component.label} pressed",


    @heroes_data.error
    @stlk_builds.error
    async def hots_handler(self, ctx, error):
        #print("Обработка ошибок hots")
        error = getattr(error, 'original', error)  # получаем пользовательские ошибки
        print(error)
        #print(type(error))
        print(f"Сообщение вызвавшее ошибку: '{ctx.message.content}' guild {ctx.guild} by {ctx.author}")
        if isinstance(error, errors.MissingRequiredArgument):
            embed = Embed(
                title="Ошибка! Введите все аргументы",
                color=config.error
            )
            embed.add_field(
                name="Пример:",
                value=f"_{config.bot_prefix}{ctx.command} Самуро_",
                inline=False
            )
            embed.set_footer(
                text=f"{config.bot_prefix}help для просмотра справки по командам"  # context.message.author если использовать без slash
            )
            await ctx.send(embed=embed)
        elif isinstance(error, exceptions.HeroNotFoundError):
            text = "Ошибка! Герой не найден"
            embed = Embed(
                title=text,
                color=config.error
            )
            embed = files.add_footer(embed)
            await ctx.send(embed=embed)


def setup(bot):
    DiscordComponents(bot)  # If you have this in an on_ready() event you can remove this line.
    bot.add_cog(Hots(bot))
