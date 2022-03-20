import json
import discord
from discord import Embed, Member, File, errors
from discord.ext import commands
from utils import check
from utils.library import files
from pprint import pprint

config = files.get_yaml()


class owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    # The below code bans player.
    @commands.command(name="user_kick")
    @check.is_owner()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)

    @commands.command(name="servers")
    async def servers(self, context):
        if context.message.author.id in config.owners:
            pprint(self.bot.guilds)
            embed = Embed(
                title='Список серверов с ботом',
                color=config.info
            )
            count = 1
            for guild in self.bot.guilds:
                embed.add_field(
                    name=f"{count}. {guild.name}",
                    value=f"Пользователей: {guild.member_count}\n",
                    inline=False
                )
                count += 1
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
        await context.author.send(embed=embed)


    @commands.command(name="shutdown")
    async def shutdown(self, context):
        """
        Make the bot shutdown
        """
        if context.message.author.id in config.owners:
            embed = Embed(
                description="Shutting down. Bye! :wave:",
                color=0x42F56C
            )
            await context.send(embed=embed)
            await self.bot.close()
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)


    @commands.command(name="say", aliases=["echo"])
    async def say(self, context, *, args):
        """
        The bot will say anything you want.
        """
        if context.message.author.id in config.owners:
            await context.send(args)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config.error
            )
            await context.send(embed=embed)

    @commands.command(name="embed")
    async def embed(self, context, *, args):
        """
        The bot will say anything you want, but within embeds.
        """
        if context.message.author.id in config.owners:
            embed = Embed(
                description=args,
                color=config.info
            )
            await context.send(embed=embed)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config.info
            )
            await context.send(embed=embed)

    @commands.command(name="serverinfo")
    @check.is_owner()
    async def serverinfo(self, context):
        """
        Get some useful (or not) information about the server.
        """
        if context.message.author.id in config.owners:
            server = context.message.guild
            roles = [x.name for x in server.roles]
            role_length = len(roles)
            if role_length > 50:
                roles = roles[:50]
                roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
            roles = ", ".join(roles)
            channels = len(server.channels)
            time = str(server.created_at)
            time = time.split(" ")
            time = time[0]

            embed = Embed(
                title="**Server Name:**",
                description=f"{server}",
                color=0x42F56C
            )
            embed.set_thumbnail(
                url=server.icon_url
            )
            embed.add_field(
                name="Owner",
                value=f"{server.owner}\n{server.owner.id}"
            )
            embed.add_field(
                name="Server ID",
                value=server.id
            )
            embed.add_field(
                name="Member Count",
                value=server.member_count
            )
            embed.add_field(
                name="Text/Voice Channels",
                value=f"{channels}"
            )
            embed.add_field(
                name=f"Roles ({role_length})",
                value=roles
            )
            embed.set_footer(
                text=f"Created at: {time}"
            )
            await context.send(embed=embed)



    @serverinfo.error
    async def owner_handler(self, ctx, error):
        error = getattr(error, 'original', error)  # получаем пользовательские ошибки
        print(error)
        #print(type(error))
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Введены не все аргументы :rolling_eyes:.')
        if isinstance(error, errors.Forbidden):
            pass  # print(error) #сообщение уже отправлено


def setup(bot):
    bot.add_cog(owner(bot))
