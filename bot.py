import discord
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1365241690893586493

BOT_NAMES = ["lala", "laclatao", "bé"]

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
        print(f"✅ {self.user} đã online")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        # ===== VC =====
        if content == "vc":
            await message.reply("Vietcong on the mic!", mention_author=False)
            return

        # ===== gọi bot =====
        if any(name in content for name in BOT_NAMES):
            await message.reply("Gọi tao hả 😏", mention_author=False)


client = MyClient()

# ===== COMMAND =====
@client.tree.command(name="ping", description="Ping test")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

client.run(TOKEN)
