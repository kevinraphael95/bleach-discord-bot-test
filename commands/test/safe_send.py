# ────────────────────────────────────────────────────────────────────────────────
# 📌 safe_test.py — Commande interactive !safe_test
# Objectif : Tester safe_send avec gestion 429
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from utils.discord_utils import safe_send

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class SafeTest(commands.Cog):
    """
    Commande !safe_test — Test de safe_send
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="safe_test",
        help="Test du safe_send pour éviter les erreurs 429",
        description="Utilise safe_send pour tester le comportement en cas de rate-limit."
    )
    async def safe_test(self, ctx: commands.Context):
        """Commande de test pour safe_send"""
        try:
            await safe_send(ctx.channel, "✅ safe_send fonctionne sans erreur 429.")
        except Exception as e:
            await ctx.send("❌ Erreur inattendue.")
            print(f"[ERREUR safe_test] {e}")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = SafeTest(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"
    await bot.add_cog(cog)
