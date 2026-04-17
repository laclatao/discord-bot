# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import requests
import os
import random

import discord
from discord import app_commands

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GUILD_ID = 1365241690893586493

# 👉 TÊN BOT (có thể đổi thoải mái)
BOT_NAMES = ["lala", "laclatao", "bé"]  # viết thường

# ===== LOG =====
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
logging.basicConfig(level=logging.INFO, handlers=[handler])

# ===== MEMORY =====
chat_history = {}
MAX_HISTORY = 15

# ===== AI =====
def chat_ai(user_id, message):
    url = "https://openrouter.ai/api/v1/chat/completions"

    if user_id not in chat_history:
        chat_history[user_id] = [
            {
                "role": "system",
                "content": (
                    "Bạn là một người bạn thân, nói chuyện tự nhiên, thân thiện, hơi hài hước. "
                    "Trả lời ngắn gọn, dễ hiểu, giống người thật. "
                    "Đôi lúc trêu nhẹ nhưng không gây khó chịu."
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
        "temperature": 0.9
    }

    res = requests.post(url, headers=headers, json=data)

    print("STATUS:", res.status_code)

    if res.status_code != 200:
        print("API ERROR:", res.text)
        return "Tao hơi lag tí 😭"

    try:
        reply = res.json()["choices"][0]["message"]["content"]
    except:
        return "API lỗi 😭"

    chat_history[user_id].append({"role": "assistant", "content": reply})

    return reply


# ===== BOT =====
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

        content = message.content.lower()

        # ===== VC =====
        if content.strip() == "vc":
            try:
                await message.delete()
            except:
                pass
            await message.reply("Vietcong on the mic!", mention_author=False)
            return

        # ===== CHECK GỌI BOT Ở BẤT KỲ ĐÂU =====
        mentioned = any(name in content for name in BOT_NAMES)

        # 👉 thêm 10% bot tự nói chuyện cho "có hồn"
        auto_chat = random.random() < 0.1

        if not mentioned and not auto_chat:
            return

        # 👉 xóa tên bot khỏi câu
        for name in BOT_NAMES:
            content = content.replace(name, "")

        content = content.strip()

        if not content:
            return

        reply = chat_ai(str(message.author.id), content[:300])

        await message.reply(reply)


client = MyClient()

# ===== COMMAND =====
@client.tree.command(name="ping", description="Ping test")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ===== RUN =====
client.run(TOKEN)