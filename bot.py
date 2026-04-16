# -*- coding: utf-8 -*-
import asyncio
import logging
from logging.handlers import RotatingFileHandler

import discord
from discord import app_commands

# ====== CONFIG ======
import os
TOKEN = os.getenv("TOKEN")

GUILD_ID = 1365241690893586493
TARGET_CHANNEL_ID = 1407065566883221504  # channel public
YOUR_ID = 123456789  # 🔥 thay bằng ID của bạn

# ====== LOGGING ======
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(fmt)
root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(handler)

# ====== BOT ======
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f"✅ Bot ready as {self.user}")
        # ❌ không gửi gì khi online

    async def on_message(self, message):
        if message.author.bot:
            return

        # 🔥 CHỈ CHO BẠN DÙNG (tránh người khác spam)
        if message.author.id != YOUR_ID:
            return

        # ====== CHAT VC ======
        if message.content.strip().lower() == "vc":
            try:
                await message.delete()
            except:
                pass

            await message.reply("Vietcong on the mic!", mention_author=False)
            return

        # ====== REPLY = BOT ANNOUNCE ======
        if message.reference:
            try:
                ref_msg = await message.channel.fetch_message(message.reference.message_id)

                target_channel = self.get_channel(TARGET_CHANNEL_ID)

                content = f"{message.content} {ref_msg.author.mention}"

                await target_channel.send(content)

                # ❌ xóa tin nhắn của bạn
                await message.delete()

            except Exception as e:
                print(e)

client = MyClient()

# ====== COMMAND ======
@client.tree.command(name="ping", description="Ping test")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ====== RUN ======
client.run(TOKEN)
