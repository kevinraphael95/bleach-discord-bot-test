# ──────────────────────────────────────────────────────────────
# 📁 REIATSU - AFFICHAGE DE SCORE
# ──────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
from supabase_client import supabase

# ──────────────────────────────────────────────────────────────
# 🔧 COG : ReiatsuCommand
# ──────────────────────────────────────────────────────────────
class ReiatsuCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  # 🔌 Référence au bot

    # ──────────────────────────────────────────────────────────
    # 💠 COMMANDE : !reiatsu [@membre]
    # ──────────────────────────────────────────────────────────
    @commands.command(
        name="reiatsu",
        aliases=["rts"],
        help="💠 Affiche le score de Reiatsu d’un membre (ou soi-même)."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # 🧊 Cooldown : 3s/user
    async def reiatsu(self, ctx: commands.Context, member: discord.Member = None):
        user = member or ctx.author  # 👤 Utilisateur ciblé (soi-même par défaut)
        user_id = str(user.id)

        # 📦 Requête vers la base de données Supabase
        data = supabase.table("reiatsu") \
                       .select("points") \
                       .eq("user_id", user_id) \
                       .execute()

        # 🎯 Extraction des points ou valeur par défaut
        points = data.data[0]["points"] if data.data else 0

        # 🖊️ Affichage du résultat
        await ctx.send(f"💠 {user.mention} a **{points}** points de Reiatsu.")

    # 🏷️ Attribution de la catégorie
    def cog_load(self):
        self.reiatsu.category = "Reiatsu"

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(ReiatsuCommand(bot))
    print("✅ Cog chargé : ReiatsuCommand (catégorie = Reiatsu)")
