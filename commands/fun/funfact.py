import discord
import json
import random
from discord.ext import commands

class FunFactCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="funfact", help="Donne un funfact sur Bleach écrit par ChatGPT.")
    async def funfact(self, ctx):
        try:
            # Lecture depuis data/funfacts_bleach.json
            with open("data/funfacts_bleach.json", "r", encoding="utf-8") as f:
                facts = json.load(f)

            if not facts:
                await ctx.send("❌ Aucun fun fact disponible.")
                return

            fact = random.choice(facts)
            await ctx.send(f"🧠 **Fun Fact Bleach :** {fact}")

        except FileNotFoundError:
            await ctx.send("❌ Fichier `funfacts_bleach.json` introuvable.")
        except Exception as e:
            await ctx.send(f"⚠️ Une erreur est survenue : {e}")

# Chargement du cog et ajout de la catégorie
async def setup(bot):
    cog = FunFactCommand(bot)
    for command in cog.get_commands():
        command.category = "Fun"
    await bot.add_cog(cog)
