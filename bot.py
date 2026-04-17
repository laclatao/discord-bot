# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import random
import requests
import os

import discord
from discord import app_commands

# ====== CONFIG ======
TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GUILD_ID = 1365241690893586493

# ====== LOGGING ======
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(fmt)
root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(handler)

# ====== AI ======
chat_history = {}

def chat_ai(user_id, message):
    url = "https://openrouter.ai/api/v1/chat/completions"

    if user_id not in chat_history:
        chat_history[user_id] = [
            {
                "role": "system",
                "content": "Bạn là bạn thân, nói chuyện kiểu Gen Z Việt Nam, hài hước, cà khịa nhẹ, trả lời ngắn gọn."
            }
        ]

    chat_history[user_id].append({"role": "user", "content": message})
    chat_history[user_id] = chat_history[user_id][-8:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openchat/openchat-7b",
        "messages": chat_history[user_id]
    }

    res = requests.post(url, headers=headers, json=data)

    print("API RESPONSE:", res.text)  # debug

    try:
        reply = res.json()["choices"][0]["message"]["content"]
    except:
        return "AI đang lag 😭"

    chat_history[user_id].append({"role": "assistant", "content": reply})

    return reply


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

    async def on_message(self, message):
        if message.author.bot:
            return

        # ===== VC =====
        if message.content.strip().lower() == "vc":
            try:
                await message.delete()
            except:
                pass
            await message.reply("Vietcong on the mic!", mention_author=False)
            return

        # ===== AI CHAT =====
        if self.user in message.mentions or random.random() < 0.3:

            # 🔥 FIX mention chuẩn
            content = message.content
            content = content.replace(f"<@{self.user.id}>", "")
            content = content.replace(f"<@!{self.user.id}>", "")
            content = content.strip()

            print("INPUT:", content)

            if not content:
                return

            reply = chat_ai(str(message.author.id), content[:200])

            await message.reply(reply)


client = MyClient()

# ===== COMMAND =====
@client.tree.command(name="ping", description="Ping test")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ===== RUN =====
client.run(TOKEN)