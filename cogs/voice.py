import discord
import asyncio
from discord.ext import commands
import traceback
import sqlite3
import validators
from utils import library
from utils.library import Const, config


class Voice(commands.Cog):
    """
    — Управление созданными голосовыми комнатами
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn, c = library.get.con_cur()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = %s", (guildID,))
        voice = c.fetchall()
        if voice is None:
            pass
        else:
            for v in voice:
                voiceID = v[0]
                try:
                    if after.channel.id == voiceID:
                        print(voiceID)
                        c.execute(
                            "SELECT * FROM voiceChannel WHERE userID = %s", (member.id,)
                        )
                        cooldown = c.fetchone()
                        if cooldown is None:
                            pass
                        else:
                            #await member.send("")
                            await asyncio.sleep(3)
                        c.execute(
                            "SELECT voiceCategoryID FROM guild WHERE guildID = %s AND voicechannelid = %s",
                            (guildID, voiceID),
                        )
                        voice = c.fetchone()
                        c.execute(
                            "SELECT channelName, channelLimit FROM userSettings WHERE userID = %s",
                            (member.id,),
                        )
                        setting = c.fetchone()
                        c.execute(
                            "SELECT channelLimit FROM guildSettings WHERE guildID = %s",
                            (guildID,),
                        )
                        guildSetting = c.fetchone()
                        if setting is None:
                            name = f"Канал {member.name}"
                            if guildSetting is None:
                                limit = 0
                            else:
                                limit = guildSetting[0]
                        else:
                            if guildSetting is None:
                                name = setting[0]
                                limit = setting[1]
                            elif guildSetting is not None and setting[1] == 0:
                                name = setting[0]
                                limit = guildSetting[0]
                            else:
                                name = setting[0]
                                limit = setting[1]
                        categoryID = voice[0]
                        id = member.id
                        category = self.bot.get_channel(categoryID)
                        channel2 = await member.guild.create_voice_channel(
                            name, category=category
                        )
                        channelID = channel2.id
                        print(type(channel2))
                        await member.move_to(channel2)
                        await channel2.set_permissions(
                            self.bot.user, connect=True, read_messages=True
                        )
                        await channel2.edit(name=name, user_limit=limit)
                        c.execute(
                            "INSERT INTO voiceChannel VALUES (%s, %s)", (id, channelID)
                        )
                        conn.commit()

                        def check(a, b, c):
                            return len(channel2.members) == 0

                        await self.bot.wait_for("voice_state_update", check=check)
                        await channel2.delete()
                        c.execute("DELETE FROM voiceChannel WHERE userID=%s", (id,))
                except:
                    pass
        conn.commit()
        conn.close()

    @commands.group()
    async def voice(self, ctx):
        pass

    @voice.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Help", description="", color=0x7289DA)
        embed.set_author(
            name=f"{ctx.guild.me.display_name}",
            url="https://discordbots.org/bot/472911936951156740",
            icon_url=f"{ctx.guild.me.avatar_url}",
        )
        embed.add_field(
            name=f"**Commands**",
            value=f"**Lock your channel by using the following command:**\n\n`.voice lock`\n\n------------\n\n"
            f"**Unlock your channel by using the following command:**\n\n`.voice unlock`\n\n------------\n\n"
            f"**Change your channel name by using the following command:**\n\n`.voice name <name>`\n\n**Example:** `.voice name EU 5kd+`\n\n------------\n\n"
            f"**Change your channel limit by using the following command:**\n\n`.voice limit number`\n\n**Example:** `.voice limit 2`\n\n------------\n\n"
            f"**Give users permission to join by using the following command:**\n\n`.voice permit @person`\n\n**Example:** `.voice permit @Sam#9452`\n\n------------\n\n"
            f"**Claim ownership of channel once the owner has left:**\n\n`.voice claim`\n\n**Example:** `.voice claim`\n\n------------\n\n"
            f"**Remove permission and the user from your channel using the following command:**\n\n`.voice reject @person`\n\n**Example:** `.voice reject @Sam#9452`\n\n",
            inline="false",
        )
        embed.set_footer(text="Bot developed by Sam#9452")
        await ctx.channel.send(embed=embed)

    @voice.command()
    async def setup(self, ctx):
        """
        - Стартовая настройка (только для владельца сервера)
        """
        conn, c = library.get.con_cur()
        guildID = ctx.guild.id
        id = ctx.author.id
        if ctx.author.id == ctx.guild.owner_id or ctx.author.id in Const.config.owners:

            def check(m):
                return m.author.id == ctx.author.id

            await ctx.channel.send("**На каждый вопрос дается 60 секунд на ответ!**")
            await ctx.channel.send(
                f"**Введите название категории, в которой вы хотите создать каналы: (например, Голосовые каналы)**"
            )
            try:
                category = await self.bot.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send("TimeoutError. Повторите команду")
            else:
                new_cat = await ctx.guild.create_category_channel(category.content)
                await ctx.channel.send(
                    "**Введите имя голосового канала: (например, Создать комнату)**"
                )
                try:
                    channel = await self.bot.wait_for(
                        "message", check=check, timeout=60.0
                    )
                except asyncio.TimeoutError:
                    await ctx.channel.send("TimeoutError. Повторите команду")
                else:
                    try:
                        channel = await ctx.guild.create_voice_channel(
                            channel.content, category=new_cat
                        )
                        c.execute(
                            "SELECT * FROM guild WHERE guildID = %s AND ownerID=%s",
                            (guildID, id),
                        )
                        voice = c.fetchone()
                        c.execute(
                            "INSERT INTO guild VALUES (%s, %s, %s, %s)",
                            (guildID, id, channel.id, new_cat.id),
                        )
                        """if voice is None:
                            c.execute ("INSERT INTO guild VALUES (%s, %s, %s, %s)",(guildID,id,channel.id,new_cat.id))
                        else:
                            c.execute ("UPDATE guild SET guildID = %s, ownerID = %s, voiceChannelID = %s, voiceCategoryID = %s WHERE guildID = %s",(guildID,id,channel.id,new_cat.id, guildID))
                        """
                        await ctx.channel.send("**Настройки завершены**")
                    except Exception as e:
                        print(e)
                        await ctx.channel.send(
                            f"Введены некоректные данные.\nИспользуйте {config.bot_prefix}voice setup еще раз!"
                        )
        else:
            await ctx.channel.send(
                f"{ctx.author.mention} только создатель сервера имеет право на эту команду"
            )
        conn.commit()
        conn.close()

    @commands.command()
    async def setlimit(self, ctx, num):
        """
        - Установить лимит на число людей в комнатах
        """
        conn, c = library.get.con_cur()
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in config.owners:
            c.execute("SELECT * FROM guildSettings WHERE guildID = %s", (ctx.guild.id,))
            voice = c.fetchone()
            if voice is None:
                c.execute(
                    "INSERT INTO guildSettings VALUES (%s, %s, %s)",
                    (ctx.guild.id, f"{ctx.author.name}'s channel", num),
                )
            else:
                c.execute(
                    "UPDATE guildSettings SET channelLimit = %s WHERE guildID = %s",
                    (num, ctx.guild.id),
                )
            await ctx.send(
                "Вы изменили лимит участников по умолчанию для вашего сервера!"
            )
        else:
            await ctx.channel.send(
                f"{ctx.author.mention} только создатель сервера имеет право на эту команду!"
            )
        conn.commit()
        conn.close()

    @voice.command()
    async def lock(self, ctx):
        """
        - Закрыть доступ к каналу
        """
        conn, c = library.get.con_cur()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = %s", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Вы не владелец комнаты")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await ctx.channel.send(f"{ctx.author.mention} Комната заблокирована 🔒")
        conn.commit()
        conn.close()

    @voice.command()
    async def unlock(self, ctx):
        """
        - Открыть доступ к каналу
        """
        conn, c = library.get.con_cur()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = %s", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Вы не владелец канала")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            await ctx.channel.send(f"{ctx.author.mention} Комната разблокирована 🔓")
        conn.commit()
        conn.close()

    @voice.command(aliases=["allow"])
    async def permit(self, ctx, member: discord.Member):
        """
        - Дать доступ пользователю на закрытый канал
        """
        conn, c = library.get.con_cur()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = %s", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Вы не владелец канала")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.channel.send(
                f"{ctx.author.mention} Вы разрешили {member.name} доступ на канал ✅"
            )
        conn.commit()
        conn.close()

    @voice.command(aliases=["deny"])
    async def reject(self, ctx, member: discord.Member):
        """
        - Блокировка доступа к каналу для выбранного пользователя
        """
        conn, c = library.get.con_cur()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = %s", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Вы не владелец канала")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute(
                        "SELECT voiceChannelID FROM guild WHERE guildID = %s",
                        (guildID,),
                    )
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False, read_messages=True)
            await ctx.channel.send(
                f"{ctx.author.mention} Вы закрыли {member.name} доступ к каналу ❌"
            )
        conn.commit()
        conn.close()

    @voice.command()
    async def limit(self, ctx, limit):
        """
        - Установить на канале лимит участников
        """
        conn, c = library.get.con_cur()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = %s", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Вы не владелец канала")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit=limit)
            await ctx.channel.send(
                f"{ctx.author.mention} Вы установили предел канала "
                + "{}!".format(limit)
            )
            c.execute("SELECT channelName FROM userSettings WHERE userID = %s", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute(
                    "INSERT INTO userSettings VALUES (%s, %s, %s)",
                    (id, f"{ctx.author.name}", limit),
                )
            else:
                c.execute(
                    "UPDATE userSettings SET channelLimit = %s WHERE userID = %s",
                    (limit, id),
                )
        conn.commit()
        conn.close()

    @voice.command()
    async def name(self, ctx, *, name):
        """
        Изменить имя канала
        """
        conn, c = library.get.con_cur()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = %s", (id,))
        voice = c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Вы не владелец канала")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name=name)
            await ctx.channel.send(
                f"{ctx.author.mention} Вы изменили имя канала на " + "{}!".format(name)
            )
            c.execute("SELECT channelName FROM userSettings WHERE userID = %s", (id,))
            voice = c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (%s, %s, %s)", (id, name, 0))
            else:
                c.execute(
                    "UPDATE userSettings SET channelName = %s WHERE userID = %s",
                    (name, id),
                )
        conn.commit()
        conn.close()

    @voice.command()
    async def claim(self, ctx):
        """
        - Получить права на управление каналом
        """
        x = False
        conn, c = library.get.con_cur()
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.channel.send(f"{ctx.author.mention} вы не в голосовом канале")
        else:
            id = ctx.author.id
            c.execute(
                "SELECT userID FROM voiceChannel WHERE voiceID = %s", (channel.id,)
            )
            voice = c.fetchone()
            if voice is None:
                await ctx.channel.send(
                    f"{ctx.author.mention} Вы не можете владеть этим каналом"
                )
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice[0])
                        await ctx.channel.send(
                            f"{ctx.author.mention} Этим каналом владеец {owner.mention}!"
                        )
                        x = True
                if x == False:
                    await ctx.channel.send(
                        f"{ctx.author.mention} Теперь вы управляете каналом"
                    )
                    c.execute(
                        "UPDATE voiceChannel SET userID = %s WHERE voiceID = %s",
                        (id, channel.id),
                    )
            conn.commit()
            conn.close()


def setup(bot):
    bot.add_cog(Voice(bot))
