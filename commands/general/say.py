# ────────────────────────────────────────────────────────────────────────────────
# 📌 say.py — Slash command /say
# Objectif : Fait répéter un message par le bot
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord import app_commands
from discord.ext import commands
from utils.discord_utils import safe_send  # ✅ Utilisation des safe_

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class SayCommand(commands.Cog):
    """
    Commande /say — Fait répéter un message par le bot
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="Le bot répète le message donné."
    )
    @app_commands.describe(message="Le message que le bot doit répéter.")
    async def say(self, interaction: discord.Interaction, message: str):
        """Commande slash /say"""

        # 🧽 Supprime l'interaction utilisateur si possible
        try:
            await interaction.response.defer(ephemeral=True, thinking=False)
        except:
            pass

        try:
            await safe_send(interaction.channel, message)
        except Exception as e:
            print(f"[ERREUR /say] {e}")
            await safe_send(interaction.channel, "❌ Une erreur est survenue en répétant le message.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = SayCommand(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.say)  # 🧠 Enregistre manuellement la slash command si nécessaire
