""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Description:
This is a template to create your own discord bot in python.
Version: 2.7
"""

import json
import os
import sys
import yaml

from helpers import sql

from discord import Embed, Member, File
from discord.ext import commands

from pprint import pprint

from helpers import json_manager

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="servers")
    async def servers(self, context):
        if context.message.author.id in config["owners"]:
            pprint(self.bot.guilds)
            embed = Embed(
                title='Список серверов с ботом',
                color=config["info"]
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


    @commands.command(name="getlog")
    async def getlog(self, ctx):
        if ctx.message.author.id in config["owners"]:
            #await ctx.author.send(file=File(config['log']))
            con = sql.get_connect()
            cur = con.cursor()
            cur.execute(
                '''SELECT * FROM logs
                    ORDER BY time DESC
                    LIMIT 50
                '''
            )
            rec = cur.fetchall()
            log = ''
            for line in rec:
                log += ' '.join(line) + '\n'
            log_name = 'main_log.log'
            with open(file=log_name, mode='w', encoding='utf-8') as log_file:
                log_file.write(log)
            await ctx.author.send(file=File(log_name))
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await ctx.send(embed=embed)


    @commands.command(name="shutdown")
    async def shutdown(self, context):
        """
        Make the bot shutdown
        """
        if context.message.author.id in config["owners"]:
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
        if context.message.author.id in config["owners"]:
            await context.send(args)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)

    @commands.command(name="embed")
    async def embed(self, context, *, args):
        """
        The bot will say anything you want, but within embeds.
        """
        if context.message.author.id in config["owners"]:
            embed = Embed(
                description=args,
                color=config["info"]
            )
            await context.send(embed=embed)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=config["error"]
            )
            await context.send(embed=embed)

    @commands.group(name="blacklist")
    async def blacklist(self, context):
        """
        Lets you add or remove a user from not being able to use the bot.
        """
        if context.invoked_subcommand is None:
            with open("blacklist.json") as file:
                blacklist = json.load(file)
            embed = Embed(
                title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
                description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                color=0x0000FF
            )
            await context.send(embed=embed)

    @blacklist.command(name="add")
    async def blacklist_add(self, context, member: Member = None):
        """
        Lets you add a user from not being able to use the bot.
        """
        if context.message.author.id in config["owners"]:
            userID = member.id
            try:
                with open("blacklist.json") as file:
                    blacklist = json.load(file)
                if (userID in blacklist['ids']):
                    embed = Embed(
                        title="Error!",
                        description=f"**{member.name}** is already in the blacklist.",
                        color=0xE02B2B
                    )
                    await context.send(embed=embed)
                    return
                json_manager.add_user_to_blacklist(userID)
                embed = Embed(
                    title="User Blacklisted",
                    description=f"**{member.name}** has been successfully added to the blacklist",
                    color=0x42F56C
                )
                with open("blacklist.json") as file:
                    blacklist = json.load(file)
                embed.set_footer(
                    text=f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await context.send(embed=embed)
            except:
                embed = Embed(
                    title="Error!",
                    description=f"An unknown error occurred when trying to add **{member.name}** to the blacklist.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @blacklist.command(name="remove")
    async def blacklist_remove(self, context, member: Member = None):
        """
        Lets you remove a user from not being able to use the bot.
        """
        if context.message.author.id in config["owners"]:
            userID = member.id
            try:
                json_manager.remove_user_from_blacklist(userID)
                embed = Embed(
                    title="User removed from blacklist",
                    description=f"**{member.name}** has been successfully removed from the blacklist",
                    color=0x42F56C
                )
                with open("blacklist.json") as file:
                    blacklist = json.load(file)
                embed.set_footer(
                    text=f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await context.send(embed=embed)
            except:
                embed = Embed(
                    title="Error!",
                    description=f"**{member.name}** is not in the blacklist.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, context):
        """
        Get some useful (or not) information about the server.
        """
        if context.message.author.id in config["owners"]:
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


def setup(bot):
    bot.add_cog(owner(bot))
