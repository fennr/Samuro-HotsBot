import os
import sys

from discord import Embed
import yaml
from discord.ext import commands

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        """
        - Список всех команд из каждого модуля
        """
        prefix = config["bot_prefix"]
        descr = "Дополнительные параметры:\n" \
                "**hero** - имя героя (ru|eng)\n" \
                "**lvl** - уровень героя\n" \
                "**btn** - клавиши способности (q|w|e|r|d)\n" \
                "**cnt** - количество (необ.)"
        white_list = [
            'hots',
            'heroes',
            'profile',
        ]
        admin_list = [
            'team',
            'event',
            'news',
        ]
        if not isinstance(prefix, str):
            prefix = prefix[0]
        embed = Embed(title="Help", description=f"{descr}", color=config["success"])
        for i in self.bot.cogs:
            if context.message.author.id in config["admins"]:
                white_list += admin_list
            if i in white_list:
                try:
                    cog = self.bot.get_cog(i.lower())
                    #commands = cog.get_commands()
                    #commands = cog.walk_commands()
                    command_list = [c.qualified_name for c in cog.walk_commands() if c.help is not None]  # [command.name for command in commands]
                    command_description = [c.help for c in cog.walk_commands() if c.help if not None]  # [command.help for command in commands]
                    help_text = '\n'.join(f'{prefix}{n} {h}' for n, h in zip(command_list, command_description))
                    embed.add_field(name=i.capitalize(), value=f'```{help_text}```', inline=False)
                except:
                    pass
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
