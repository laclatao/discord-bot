import discord
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

# 👉 ID server của bạn
GUILD_ID = 1365241690893586493

# 👉 từ khóa gọi bot
BOT_NAMES = ["lala", "laclatao", "bé"]


class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        synced = await self.tree.sync(guild=guild)
        print(f"✅ Đã sync {len(synced)} lệnh")

    async def on_ready(self):
        print(f"🤖 Bot online: {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        # ===== lệnh "vc"
        if content == "vc":
            await message.reply("Vietcong on the mic!", mention_author=False)
            return

        # ===== gọi tên bot
        if any(name in content for name in BOT_NAMES):
            await message.reply("Gọi tao hả 😏", mention_author=False)


client = MyClient()


# ===== SLASH COMMAND =====
@client.tree.command(
    name="ping",
    description="Ping test",
    guild=discord.Object(id=GUILD_ID)  # 👉 QUAN TRỌNG
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")


# ===== RUN =====
client.run(TOKEN)
