# ──────────────────────────────────────────────────────────────
# 📁 CODE
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands

# ──────────────────────────────────────────────────────────────
# 🧠 COG : Classe de commande
# ──────────────────────────────────────────────────────────────
class CodeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────
    # 💬 COMMANDE : !code
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="code",
        help="Affiche le lien vers le code source du bot sur GitHub."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def code(self, ctx: commands.Context):
        await ctx.send("🔗 Code source du bot : https://github.com/kevinraphael95/bleach-discord-bot-test")

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP : Fonction de chargement du COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = CodeCommand(bot)
    await bot.add_cog(cog)
    
    # 📌 Attribution de la catégorie ici (après ajout)
    if hasattr(cog, "code"):
        cog.code.category = "Général"

    print("✅ Cog chargé : CodeCommand (catégorie = Général)")
