# ────────────────────────────────────────────────────────────────────────────────
# 📌 carre_animé.py — Commande interactive !carre
# Objectif : Affiche un carré qui change de taille en boucle pendant 25 secondes
# Catégorie : Test
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import asyncio

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class CarreAnime(commands.Cog):
    """
    Commande !carre — Affiche un carré animé pendant 25 secondes
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="carre",
        help="Affiche un carré qui change de taille pendant 25 secondes.",
        description="Anime un carré en boucle toutes les secondes, dans un message Discord."
    )
    async def carre(self, ctx: commands.Context):
        """Commande principale qui affiche un carré changeant."""
        formes = ["▫️", "◽", "◻️", "⬜", "◻️", "◽"]
        message = await ctx.send(formes[0])

        try:
            for i in range(25):
                index = i % len(formes)
                await message.edit(content=formes[index])
                await asyncio.sleep(1)

            await message.edit(content="✅ Animation terminée !")
        except Exception as e:
            print(f"[ERREUR !carre] {e}")
            await ctx.send("❌ Une erreur est survenue pendant l'animation.")


# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = CarreAnime(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
