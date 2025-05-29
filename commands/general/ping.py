# ──────────────────────────────────────────────────────────────
# 📁 PING
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands

# ──────────────────────────────────────────────────────────────
# 🔧 COG : PingCommand
# ──────────────────────────────────────────────────────────────
class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # 🔌 Stocke la référence du bot

    # ──────────────────────────────────────────────────────────
    # 💬 COMMANDE : !ping (alias : !test)
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="ping",
        aliases=["test"],  # ✅ Alias accepté : !test
        help="Répond avec la latence du bot."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # ⏱️ Cooldown anti-spam (3s par user)
    async def ping(self, ctx: commands.Context):
        # 📡 Calcul de la latence en millisecondes
        latence = round(self.bot.latency * 1000)

        # 🎨 Création de l'embed de réponse
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"📶 Latence : `{latence} ms`",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    # ──────────────────────────────────────────────────────────
    # 🏷️ CATEGORISATION AUTOMATIQUE
    # ──────────────────────────────────────────────────────────
    def cog_load(self):
        self.ping.category = "Général"  # 📁 Utilisé par !commandes et !help

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGER LE COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(PingCommand(bot))
    print("✅ Cog chargé : PingCommand (catégorie = Général)")
