from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from cogs import general, help, hots, heroes, profile

guild_ids = [845658540341592096]  # Сервер ID для тестирования


class Slash(commands.Cog, name="slash"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="profile", description="Батлнет профиль")
    async def slash_profile(self, ctx: SlashContext, user):
        await profile.Profile.profile_info(self, ctx, user)

    @cog_ext.cog_slash(name="add", description="Добавить профиль")
    async def slash_add(self, ctx: SlashContext, battletag, user):
        await profile.Profile.profile_add(self, ctx, battletag, user)

    @cog_ext.cog_slash(name="info", description="Описание бота")
    async def slash_info(self, ctx: SlashContext):
        await general.general.info(self, ctx)

    @cog_ext.cog_slash(name="weekly", description="Список героев еженедельной ротации")
    async def slash_rotate(self, ctx: SlashContext):
        await heroes.Heroes.rotation(self, ctx)

    @cog_ext.cog_slash(name="ban", description="Список рекомендуемых к бану героев")
    async def slash_ban(self, ctx: SlashContext):
        await heroes.Heroes.ban_list(self, ctx)

    '''@cog_ext.cog_slash(name="data", description="Полные данные по герою")
    async def slash_data(self, ctx: SlashContext, hero):
        await heroes.Heroes.data(self, ctx, hero)'''

    @cog_ext.cog_slash(name="streams", description="Онлайн стримы на твиче")
    async def slash_streams(self, ctx: SlashContext, cnt):
        await heroes.Heroes.streams(self, ctx, cnt)

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

    @cog_ext.cog_slash(name="patchnotes", description="Описание последнего обновления")
    async def slash_pn(self, ctx: SlashContext):
        await hots.hots.hots_notes(self, ctx)

    @cog_ext.cog_slash(name="stlk", description="Билды от Сталка")
    async def slash_stlk_builds(self, ctx: SlashContext, hero):
        await heroes.Heroes.stlk_builds(self, ctx, hero)


def setup(bot):
    bot.add_cog(Slash(bot))
