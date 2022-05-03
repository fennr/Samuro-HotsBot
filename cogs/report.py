import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import command, Cog, errors
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
from discord_slash.context import ComponentContext
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

    @command(name='select')
    async def select_test(self, ctx):
        select = Select(
            options=[  # the options in your dropdown
                SelectOption(label="Выбор 1", value="v1", emoji="🥼"),
                SelectOption(label="Выбор 2", value="v2", emoji="🧪"),
                SelectOption(label="Выбор 3", value="v2", emoji="🧫"),
            ],
            placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=2,  # the maximum number of options a user can select
        )
        await ctx.message.delete()
        await ctx.send("test", components=[select])

    @Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        # ctx.selected_options is a list of all the values the user selected
        await ctx.send(content=f"You selected {ctx.selected_options}")

    @Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.component.label == labels['Close']:
            print(interaction.raw_data)
            # await interaction.channel.delete()
        if interaction.component.label in labels['Questions'].values():
            category = discord.utils.get(interaction.guild.categories, name=TICKET_CATEGORY)
            name = f"{interaction.component.label}-{interaction.author.name}"
            channel = await interaction.guild.create_text_channel(name, category=category, sync_permissions=True)
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = True
            overwrite.read_messages = True
            await channel.set_permissions(target=interaction.author, overwrite=overwrite)
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
