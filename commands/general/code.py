# ────────────────────────────────────────────────────────────────────────────────
# 📌 code.py — Commande !code
# Objectif : Affiche le lien vers le code source du bot
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from utils.discord_utils import safe_send  # ✅ Utilisation sécurisée

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class CodeCommand(commands.Cog):
    """
    Commande !code — Affiche le lien du code source du bot
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="code",
        help="Affiche le lien vers le code source du bot sur GitHub.",
        description="Envoie un lien vers le dépôt GitHub contenant le code du bot."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def code(self, ctx: commands.Context):
        """Affiche le lien vers le code source."""
        try:
            await safe_send(ctx.channel, "🔗 Code source du bot : https://github.com/kevinraphael95/bleach-discord-bot-test")
        except Exception as e:
            print(f"[ERREUR !code] {e}")
            await safe_send(ctx.channel, "❌ Une erreur est survenue en envoyant le lien du code.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = CodeCommand(bot)
    await bot.add_cog(cog)
    
    # 📌 Attribution de la catégorie ici
    if hasattr(cog, "code"):
        cog.code.category = "Général"
