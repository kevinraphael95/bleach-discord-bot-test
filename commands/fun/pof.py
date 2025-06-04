# ────────────────────────────────────────────────────────────────
#       🪙 COMMANDE DISCORD - PILE OU FACE        
# ────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import random
from discord.ext import commands

# ────────────────────────────────────────────────────────────────═
# 🎲 Classe de la commande "pof"
# ────────────────────────────────────────────────────────────────═
class PofCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ───────────────────────────────────────────────
    # 🪙 Commande !pof : pile ou face
    # ⏱️ Cooldown utilisateur de 3 secondes
    # ───────────────────────────────────────────────
    @commands.command(
        name="pof",
        aliases=["pileouface"],
        help="🪙 Lance une pièce : pile ou face."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def pof(self, ctx):
        resultat = random.choice(["🪙 Pile !", "🪙 Face !"])
        await ctx.send(resultat)

    # ✅ Attribution à la catégorie "Fun"
    def cog_load(self):
        self.pof.category = "Fun"

# ────────────────────────────────────────────────────────────────═
# 🔌 Setup du module pour ajout automatique au bot
# ────────────────────────────────────────────────────────────────═
async def setup(bot):
    cog = PofCommand(bot)
    for command in cog.get_commands():
        command.category = "Fun"
    await bot.add_cog(cog)
