# ────────────────────────────────────────────────────────────────────────────────
# 📌 funfact_bleach.py — Commande interactive !funfact
# Objectif : Donne un fun fact sur Bleach écrit par ChatGPT
# Catégorie : 🧠 Fun
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import random
import os

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des données JSON
# ────────────────────────────────────────────────────────────────────────────────
DATA_JSON_PATH = os.path.join("data", "funfacts_bleach.json")

def load_data():
    """Charge les fun facts depuis le fichier JSON."""
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class FunFactCommand(commands.Cog):
    """
    Commande !funfact — Donne un fun fact sur Bleach écrit par ChatGPT.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="funfact",
        help="🧠 Donne un fun fact sur Bleach écrit par ChatGPT.",
        description="Affiche un fait intéressant aléatoire tiré d'un fichier JSON."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def funfact(self, ctx: commands.Context):
        """Commande principale qui envoie un fun fact aléatoire."""
        try:
            facts = load_data()
            if not facts:
                await ctx.send("❌ Aucun fun fact disponible.")
                return

            fact = random.choice(facts)
            await ctx.send(f"🧠 **Fun Fact Bleach :** {fact}")

        except FileNotFoundError:
            await ctx.send("❌ Fichier `funfacts_bleach.json` introuvable.")
        except Exception as e:
            await ctx.send(f"⚠️ Une erreur est survenue : {e}")

    def cog_load(self):
        self.funfact.category = "Fun"

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(FunFactCommand(bot))
