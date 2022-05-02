import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import command, Cog, errors
from discord_components import DiscordComponents, Button, ButtonStyle
from utils import check
from utils.classes.Const import config

labels = {
    'Questions': {
        'Error': 'Ошибка',
        'Question': 'Вопрос',
        'Report': 'Жалоба',
        'Offer': 'Предложение',
    },
    'Close': 'Закрыть тикет'
}

TICKET_CATEGORY = 'Tickets'

menu_buttons = [
    # Button(style=ButtonStyle.gray, label=labels['Error'],),
    Button(style=ButtonStyle.gray, label=labels['Questions']['Question']),
    Button(style=ButtonStyle.gray, label=labels['Questions']['Report']),
    Button(style=ButtonStyle.gray, label=labels['Questions']['Offer']),
]

remove_button = [
    Button(style=ButtonStyle.red, label=labels['Close'])
]


class Report(commands.Cog, name="Report"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='create_rep')
    @check.is_owner()
    async def create_report(self, ctx):
        message = 'Воспользовавшись кнопками ниже можно связаться с модерацией по интересующим вопросам'
        embed = Embed(
            title='Поддержка',
            description=message,
            color=config.success
        )
        await ctx.message.delete()
        await ctx.send(embed=embed, components=[menu_buttons])

    @Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.component.label == labels['Close']:
            await interaction.channel.delete()
        if interaction.component.label in labels['Questions'].values():
            category = discord.utils.get(interaction.guild.categories, name=TICKET_CATEGORY)
            overwrites = {
                interaction.author: discord.PermissionOverwrite(send_messages=True)
            }
            name = f"{interaction.component.label}-{interaction.author.name}"
            channel = await interaction.guild.create_text_channel(name, category=category, overwrites=overwrites)
            ticket_created_embed = discord.Embed(
                title="Заявка открыта",
                description=f"""Привет {interaction.author.name}! Опиши в чате ниже подробно проблему и ближайшее время тебе ответит модератор.
                    Если вопрос решен, заявку можно закрыть нажав кнопку ниже""",
            )
            await channel.send(
                interaction.author.mention, embed=ticket_created_embed, components=[remove_button]
            )  # ping the user who pressed the button, and send the embed
        try:
            await interaction.respond()
        except:
            pass


def setup(bot):
    bot.add_cog(Report(bot))
