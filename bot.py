# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import requests
import os

import discord
from discord import app_commands

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GUILD_ID = 1365241690893586493

BOT_NAMES = ["lala", "bé", "laclatao"]

# ===== LOG =====
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
logging.basicConfig(level=logging.INFO, handlers=[handler])

# ===== MEMORY =====
chat_history = {}
MAX_HISTORY = 6  # 🔥 ít lại cho đỡ loạn

# ===== AI =====
def chat_ai(user_id, message):
    url = "https://openrouter.ai/api/v1/chat/completions"

    if user_id not in chat_history:
        chat_history[user_id] = [
            {
                "role": "system",
                "content": (
                    "Bạn là một người bạn thân. "
                    "Luôn trả lời bằng tiếng Việt. "
                    "Nói tự nhiên, dễ hiểu, giống chat ngoài đời. "
                    "Trả lời ngắn gọn 1-2 câu. "
                    "Không dùng tiếng Anh hoặc ngôn ngữ khác."
                )
            }
        ]

    chat_history[user_id].append({"role": "user", "content": message})
    chat_history[user_id] = chat_history[user_id][-MAX_HISTORY:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": chat_history[user_id],
        "temperature": 0.7,   # 🔥 giảm cho ổn định
        "max_tokens": 60
    }

    res = requests.post(url, headers=headers, json=data)

    if res.status_code != 200:
        print("API ERROR:", res.text)
        return "hơi lag tí 😅"

    try:
        reply = res.json()["choices"][0]["message"]["content"]
    except:
        return "lỗi tí 😅"

    chat_history[user_id].append({"role": "assistant", "content": reply})

    return reply.strip()


# ===== BOT =====
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

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

        content = message.content.lower()

        # ===== CHECK REPLY BOT =====
        is_reply = False
        if message.reference:
            try:
                msg = await message.channel.fetch_message(message.reference.message_id)
                if msg.author.id == self.user.id:
                    is_reply = True
            except:
                pass

        # ===== CHECK GỌI TÊN =====
        mentioned = any(name in content for name in BOT_NAMES)

        if not mentioned and not is_reply:
            return

        # xóa tên bot
        for name in BOT_NAMES:
            content = content.replace(name, "")

        content = content.strip()

        if not content:
            return

        reply = chat_ai(str(message.author.id), content[:200])

        await message.reply(reply)


client = MyClient()

# ===== COMMAND =====
@client.tree.command(name="ping", description="Ping test")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

# ===== RUN =====
client.run(TOKEN)