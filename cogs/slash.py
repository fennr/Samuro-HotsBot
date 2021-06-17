import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from cogs import general, help, hots

guild_ids = [845658540341592096]  # Сервер ID для тестирования


class Slash(commands.Cog, name="slash"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="info", description="Описание бота")
    async def slash_info(self, ctx: SlashContext):
        await general.general.info(self, ctx)

    @cog_ext.cog_slash(name="invite", description="Пригласить бота на свой канал")
    async def slash_invite(self, ctx: SlashContext):
        await general.general.invite(self, ctx)

    @cog_ext.cog_slash(name="help", description="Все доступные команды")
    async def slash_help(self, ctx: SlashContext):
        await help.Help.help(self, ctx)

    @cog_ext.cog_slash(name="hero", description="Описание героя")
    async def slash_hero(self, ctx: SlashContext, hero):
        await hots.hots.hots_hero(self, ctx, hero)

    @cog_ext.cog_slash(name="skill", description="Описание скиллов героя")
    async def slash_skill(self, ctx: SlashContext, hero):
        await hots.hots.hots_skill(self, ctx, hero)

    @cog_ext.cog_slash(name="talent", description="Описание талантов героя %lvl% уровня")
    async def slash_talent(self, ctx: SlashContext, hero, lvl):
        await hots.hots.hots_talent(self, ctx, hero, lvl)



def setup(bot):
    bot.add_cog(Slash(bot))
