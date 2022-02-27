import os
import yaml
from discord import Embed, utils
from discord.ext import commands
from discord.errors import Forbidden

if not os.path.isfile("config.yaml"):
    # sys.exit("'config.yaml' not found! Please add it and try again.")
    with open("../config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


clear = '\u200b'

class Ruhots(commands.Cog):
    """
    — Команды для сервера RU Heroes of the Storm
    """

    @commands.command(name="test_art")
    @commands.has_role("🎨 Художник")
    async def test_art(self, ctx):
        await ctx.send("Проверка роли художник пройдена")

    @commands.command(name="art")
    @commands.has_role("🎨 Художник")
    async def art(self, ctx, message=None):
        """
        — Выложить арт в исскуство
        """
        like = utils.get(ctx.guild.emojis, name="samuro")
        dislike = utils.get(ctx.guild.emojis, name="dislike")
        if ctx.guild.id == 642852514865217578:  # RU hots
            art_id = 708678722127134810
        elif ctx.guild.id == 754063467610374224:  # RU HS
            art_id = 766035868321710081
        else:
            art_id = 845658540341592099
        if like is None:
            like = '\N{THUMBS UP SIGN}'
            dislike = '\N{THUMBS DOWN SIGN}'
        art_channel = utils.get(ctx.guild.channels, id=art_id)
        if message is not None:
            description = f"**Автор:** {ctx.author.mention}\n**Комментарий:** {message}"
        else:
            description = f"**Автор:** {ctx.author.mention}"
        if ctx.message.attachments:
            embed = Embed(
                title="Новый арт!",
                description=description,
                color=config["info"]
            )
            url = ctx.message.attachments[0].url
            embed.set_image(url=url)
            msg = await art_channel.send(embed=embed)
            await msg.add_reaction(emoji=like)
            await msg.add_reaction(emoji=dislike)
        else:
            await ctx.send("Вы забыли добавить изображение")

    @test_art.error
    @art.error
    async def ruhots_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingRole):
            await ctx.send("Требуется Роль 'Художник'")


def setup(bot):
    bot.add_cog(Ruhots(bot))