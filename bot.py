# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import requests
import os
import random
import re
import json

import discord
from discord import app_commands

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GUILD_ID = 1365241690893586493

BOT_NAMES = ["lala", "bé", "laclatao"]

# 👉 ID người được simp (đổi thành ID của bạn bè bạn)
SIMP_USER_ID = 123456789012345678  # <-- sửa

# ===== LOG =====
handler = RotatingFileHandler("bot.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
logging.basicConfig(level=logging.INFO, handlers=[handler])

# ===== MEMORY FILE =====
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

memory = load_memory()

# ===== CHAT HISTORY =====
chat_history = {}
MAX_HISTORY = 8

# ===== CLEAN =====
def clean_reply(text: str) -> str:
    if re.search(r"[А-Яа-яЁёÜüß]", text):
        return "nãy nói nhảm tí :v"
    return text.strip()

# ===== MOOD SYSTEM =====
MOODS = ["vui", "lạnh", "lầy"]

def get_user_mood(user_id):
    user_id = str(user_id)
    if user_id not in memory:
        memory[user_id] = {
            "mood": random.choice(MOODS),
            "name": None
        }
    return memory[user_id]["mood"]

def set_random_mood(user_id):
    if random.random() < 0.2:
        memory[str(user_id)]["mood"] = random.choice(MOODS)

# ===== AI =====
def build_system_prompt(user_id):
    mood = get_user_mood(user_id)

    base = (
        "Mày là bạn thân, nói chuyện như người thật ngoài đời. "
        "Luôn dùng tiếng Việt. "
        "Trả lời 1-2 câu, tự nhiên, có cảm xúc. "
        "Không nói kiểu AI."
    )

    if mood == "vui":
        base += " Giọng vui vẻ, thoải mái, hơi hài."
    elif mood == "lạnh":
        base += " Nói ngắn, hơi lạnh, ít cảm xúc."
    elif mood == "lầy":
        base += " Nói lầy, hơi cà khịa nhẹ."

    # simp mode
    if int(user_id) == SIMP_USER_ID:
        base += " Người này là người mày thích, nói chuyện dịu dàng hơn, quan tâm hơn một chút."

    return base

def chat_ai(user_id, message):
    url = "https://openrouter.ai/api/v1/chat/completions"

    if user_id not in chat_history:
        chat_history[user_id] = [
            {"role": "system", "content": build_system_prompt(user_id)}
        ]

    # update mood random
    set_random_mood(user_id)

    chat_history[user_id][0] = {
        "role": "system",
        "content": build_system_prompt(user_id)
    }

    chat_history[user_id].append({"role": "user", "content": message})
    chat_history[user_id] = chat_history[user_id][-MAX_HISTORY:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": chat_history[user_id],
        "temperature": 0.9,
        "max_tokens": 80
    }

    res = requests.post(url, headers=headers, json=data)

    if res.status_code != 200:
        return "lag tí 😭"

    try:
        reply = res.json()["choices"][0]["message"]["content"]
        reply = clean_reply(reply)
    except:
        return "lỗi 😭"

    chat_history[user_id].append({"role": "assistant", "content": reply})

    return reply

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

        user_id = str(message.author.id)
        content = message.content.lower()

        # ===== CHECK REPLY =====
        is_reply = False
        if message.reference:
            try:
                msg = await message.channel.fetch_message(message.reference.message_id)
                if msg.author.id == self.user.id:
                    is_reply = True
            except:
                pass

        # ===== CHECK NAME =====
        mentioned = any(name in content for name in BOT_NAMES)

        if not mentioned and not is_reply:
            return

        # remove name
        for name in BOT_NAMES:
            content = content.replace(name, "")

        content = content.strip()
        if not content:
            return

        reply = chat_ai(user_id, content[:200])

        save_memory(memory)

        await message.reply(reply)


client = MyClient()

@client.tree.command(name="ping", description="Ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

client.run(TOKEN)