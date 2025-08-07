# ────────────────────────────────────────────────────────────────────────────────
# 📌 say.py — Commande interactive /say
# Objectif : Faire répéter un message par le bot en slash command
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord import app_commands
from discord.ext import commands
from utils.discord_utils import safe_send, safe_respond  # ✅ Utilisation des safe_

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Say(commands.Cog):
    """
    Commande /say — Faire répéter un message par le bot (slash)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="Le bot répète le message donné."
    )
    @app_commands.describe(message="Message à faire répéter")
    async def slash_say(self, interaction: discord.Interaction, message: str):
        """Commande slash principale qui fait répéter un message."""
        try:
            await safe_send(interaction.channel, message)
            await safe_respond(interaction, "Message envoyé !", ephemeral=True)
        except Exception as e:
            print(f"[ERREUR /say] {e}")
            await safe_respond(interaction, "❌ Une erreur est survenue en répétant le message.", ephemeral=True)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Say(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"
    await bot.add_cog(cog)
