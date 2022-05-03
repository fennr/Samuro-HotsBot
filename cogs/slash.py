""""
Samuro Bot

Автор: *fennr*
github: https://github.com/fennr/Samuro-HotsBot

Бот для сообществ по игре Heroes of the Storm

"""
import discord
from discord.commands import CommandPermission, SlashCommandGroup
from discord.ext import commands

from cogs import general, help, heroes, hots, profile, event, voice
from utils import check, exceptions

guild_ids = [845658540341592096]  # Сервер ID для тестирования


class Slash(commands.Cog, name="Slash"):
    def __init__(self, bot):
        self.bot = bot

    greetings = SlashCommandGroup("greetings", "Various greeting from cogs!")

    international_greetings = greetings.create_subgroup("international", "International greetings")

    secret_greetings = SlashCommandGroup(
        "secret_greetings",
        "Secret greetings",
        permissions=[CommandPermission("owner", 2, True)],  # Ensures the owner_id user can access this, and no one else
    )

    @greetings.command(guild_ids=guild_ids)
    async def hello(self, ctx):
        await ctx.respond("Hello, this is a slash subcommand from a cog!")

    @international_greetings.command(guild_ids=guild_ids)
    async def aloha(self, ctx):
        await ctx.respond("Aloha, a Hawaiian greeting")

    @secret_greetings.command(guild_ids=guild_ids)
    async def secret_handshake(self, ctx, member: discord.Member):
        await ctx.respond(f"{member.mention} secret handshakes you")

    '''@cog_ext.cog_slash(name="voice_name", description="Переименовать комнату")
    async def slash_voice_name(self, ctx: SlashContext, name):
        await voice.Voice.name(self, ctx, name=name)

    @cog_ext.cog_slash(name="voice_limit", description="Установить лимит участников")
    async def slash_voice_limit(self, ctx: SlashContext, limit):
        await voice.Voice.limit(self, ctx, limit=limit)

    @cog_ext.cog_slash(name="voice_lock", description="Сделать комнату закрытой")
    async def slash_voice_lock(self, ctx: SlashContext):
        await voice.Voice.lock(self, ctx)

    @cog_ext.cog_slash(name="voice_unlock", description="Сделать комнату открытой")
    async def slash_voice_unlock(self, ctx: SlashContext):
        await voice.Voice.unlock(self, ctx)

    @cog_ext.cog_slash(name="profile", description="Профиль игрока")
    async def slash_profile(self, ctx: SlashContext, user):
        await profile.Profile.profile_info(self, ctx, user)

    @cog_ext.cog_slash(name="login", description="Авторизоваться на сервере")
    async def slash_login(self, ctx: SlashContext, battletag):
        await profile.Profile.login(self, ctx, battletag)

    @cog_ext.cog_slash(name="5x5", description="Подбор команд")
    @check.is_admin()
    async def slash_5x5(self, ctx: SlashContext, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10):
        await event.Event.event_5x5(self, ctx, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)

    @cog_ext.cog_slash(name="profile_add",
                       description="Добавить профиль",
                       options=[
                           create_option(
                               name="battletag",
                               description="Введите батлтег",
                               option_type=3,
                               required=True,
                           ),
                           create_option(
                               name="discord",
                               description="Введите дискорд через упоминание",
                               option_type=3,
                               required=True,
                           )
                       ]
                       )
    async def slash_add(self, ctx: SlashContext, battletag: str, discord: Member):
        await profile.Profile.profile_add(self, ctx, btag=battletag, discord_user=discord)

    @cog_ext.cog_slash(name="info", description="Описание бота")
    async def slash_info(self, ctx: SlashContext):
        await general.general.info(self, ctx)

    @cog_ext.cog_slash(name="avatar", description="Вывести аватар")
    async def slash_avatar(self, ctx:SlashContext, member: Member):
        await general.general.avatar(self, ctx, member)

    @cog_ext.cog_slash(name="weekly", description="Список героев еженедельной ротации")
    async def slash_rotate(self, ctx: SlashContext):
        await hots.Hots.rotation(self, ctx)

    @cog_ext.cog_slash(name="ban", description="Список рекомендуемых к бану героев")
    async def slash_ban(self, ctx: SlashContext):
        await hots.Hots.ban_list(self, ctx)

    @cog_ext.cog_slash(name="data", description="Полные данные по герою")
    async def slash_data(self, ctx: SlashContext, hero):
        await hots.Hots.heroes_data(self, ctx, hero)

    @cog_ext.cog_slash(name="streams", description="Онлайн стримы на твиче")
    async def slash_streams(self, ctx: SlashContext, cnt):
        await hots.Hots.streams(self, ctx, cnt)

    @cog_ext.cog_slash(name="invite", description="Пригласить бота на свой канал")
    async def slash_invite(self, ctx: SlashContext):
        await general.general.invite(self, ctx)

    @cog_ext.cog_slash(name="help", description="Все доступные команды")
    async def slash_help(self, ctx: SlashContext, unit):
        await help.Help.help(self, ctx, unit)

    @cog_ext.cog_slash(name="hero", description="Описание героя")
    async def slash_hero(self, ctx: SlashContext, hero):
        await heroes.Heroes.hots_hero(self, ctx, hero)

    @cog_ext.cog_slash(name="skill", description="Описание скиллов героя")
    async def slash_skill(self, ctx: SlashContext, hero):
        await heroes.Heroes.hots_skill(self, ctx, hero)

    @cog_ext.cog_slash(name="talent", description="Описание талантов героя %lvl% уровня")
    async def slash_talent(self, ctx: SlashContext, hero, lvl):
        await heroes.Heroes.hots_talent(self, ctx, hero, lvl)

    @cog_ext.cog_slash(name="patchnotes", description="Описание последнего обновления")
    async def slash_pn(self, ctx: SlashContext):
        await hots.Hots.hots_notes(self, ctx)

    @cog_ext.cog_slash(name="stlk", description="Билды от Сталка")
    async def slash_stlk_builds(self, ctx: SlashContext, hero):
        await hots.Hots.stlk_builds(self, ctx, hero)'''


def setup(bot):
    bot.add_cog(Slash(bot))
