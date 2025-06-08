# ────────────────────────────────────────────────────────────────────────────────
# 📌 destin.py — Commande interactive !destin
# Objectif : Tire ton destin absurde dans l’univers de Bleach
# Catégorie : Test
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import os
import random

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement du fichier JSON des destins
# ────────────────────────────────────────────────────────────────────────────────
DESTIN_PATH = os.path.join("data", "destins_bleach.json")

def charger_destins():
    with open(DESTIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Destin(commands.Cog):
    """
    Commande !destin — Tire ton destin absurde dans l’univers de Bleach.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.destins = charger_destins()

    @commands.command(
        name="destin",
        help="Tire ton destin absurde dans l’univers de Bleach.",
        description="Affiche une phrase de mort, une réincarnation absurde, et un événement improbable."
    )
    async def destin(self, ctx: commands.Context):
        """Commande principale qui génère un destin en 3 phrases absurdes."""
        mort = random.choice(self.destins["morts"])
        reincarn = random.choice(self.destins["reincarnations"])
        evenement = random.choice(self.destins["evenements"])

        await ctx.send(
            f"🕊️ **Ton destin est scellé...**\n{mort}\n{reincarn}\n{evenement}"
        )

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Destin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
