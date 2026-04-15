# -*- coding: utf-8 -*-
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

import discord
from discord import app_commands

# ====== CONFIG ======
import os
TOKEN = os.getenv("TOKEN")  # dùng Railway Variables
GUILD_ID = 1365241690893586493
CHANNEL_ID = 1407065566883221504
STARTUP_MESSAGE = "Vietcong on the mic!"

# ====== LOGGING ======
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(fmt)
root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(handler)
logging.getLogger("discord").setLevel(logging.INFO)

# ====== BOT ======
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # để dùng chat "vc"
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print(f"✅ Slash command đã sync trong server {GUILD_ID}")

    async def on_ready(self):
        print(f"✅ Bot ready as {self.user}")

        if not self.synced:
            guild = discord.Object(id=GUILD_ID)
            await self.tree.sync(guild=guild)
            self.synced = True

        await asyncio.sleep(2)
        try:
            channel = await self.fetch_channel(CHANNEL_ID)
            await channel.send(STARTUP_MESSAGE)
        except Exception as e:
            print(f"❌ Lỗi gửi startup message: {e}")

    # 🔥 CHAT "vc" + XÓA TIN NHẮN
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.strip().lower() == "vc":
            try:
                await message.delete()
            except:
                pass
            await message.channel.send("Vietcong on the mic!")

client = MyClient()
GUILD = discord.Object(id=GUILD_ID)

# ====== COMMANDS ======

@client.tree.command(name="ping", description="Trả lời Pong!", guild=GUILD)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@client.tree.command(name="hello", description="Chào theo tên bạn nhập", guild=GUILD)
@app_commands.describe(name="Tên của bạn")
async def hello(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"👋 Hello {name}!")

# ====== ANNOUNCE ======
ALLOWED = discord.AllowedMentions(
    everyone=True,
    roles=True,
    users=True,
    replied_user=False
)

@client.tree.command(name="announce", description="Gửi thông báo + tag", guild=GUILD)
@app_commands.describe(
    channel="Kênh sẽ đăng",
    message="Nội dung thông báo",
    user="Tag một thành viên",
    role="Tag một role"
)
async def announce(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str,
    user: Optional[discord.Member] = None,
    role: Optional[discord.Role] = None,
):
    await interaction.response.defer()

    mentions = []

    if user:
        mentions.append(user.mention)

    if role:
        mentions.append(role.mention)

    # 🔥 TAG RA SAU
    content = f"{message} {' '.join(mentions)}" if mentions else message

    try:
        await channel.send(content, allowed_mentions=ALLOWED)
        await interaction.followup.send("✅ Đã gửi!")
    except Exception as e:
        await interaction.followup.send(f"❌ Lỗi: {e}")

# ====== RUN ======
client.run(TOKEN)