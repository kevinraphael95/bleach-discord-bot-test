# ────────────────────────────────────────────────────────────────
#        🐶 COMMANDE DISCORD - CHIEN ALÉATOIRE        
# ────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import aiohttp
import discord
from discord.ext import commands

# ────────────────────────────────────────────────────────────────═
# 📦 Classe principale de la commande "dog"
# ────────────────────────────────────────────────────────────────═
class DogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ───────────────────────────────────────────────
    # 🐕 Commande !dog : affiche une image de chien
    # Cooldown : 1 fois toutes les 3 secondes par utilisateur
    # ───────────────────────────────────────────────
    @commands.command(
        name="dog",
        help="🐶 Affiche une photo aléatoire d’un chien."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def dog(self, ctx):
        # 🌐 Requête vers l'API Dog CEO
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as response:
                # ✅ Si la réponse est OK
                if response.status == 200:
                    data = await response.json()
                    image_url = data["message"]

                    # 📤 Envoi de l’image dans le salon
                    await ctx.send(f"Voici un toutou aléatoire ! 🐶\n{image_url}")
                else:
                    # ❌ En cas d’erreur API
                    await ctx.send("❌ Impossible de récupérer une image de chien 😢")

    # 📁 Attribution de la catégorie "Fun"
    def cog_load(self):
        self.dog.category = "Fun"

# ────────────────────────────────────────────────────────────────═
# 🔌 Fonction de setup pour charger le Cog
# ────────────────────────────────────────────────────────────────═
async def setup(bot):
    await bot.add_cog(DogCommand(bot))
