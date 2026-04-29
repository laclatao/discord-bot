# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import os

import discord
from discord import app_commands

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
GUILD_ID = 1365241690893586493

# ===== LOG =====
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
logging.basicConfig(level=logging.INFO, handlers=[handler])

# ===== BOT =====
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # vẫn bật nhưng không dùng

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f"✅ Bot ready as {self.user}")

    # 🔥 TẮT HOÀN TOÀN CHAT AI
    async def on_message(self, message):
        return


client = MyClient()

# ===== COMMAND =====
@client.tree.command(name="ping", description="Ping test")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ===== RUN =====
client.run(TOKEN)
