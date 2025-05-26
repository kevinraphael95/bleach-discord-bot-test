import discord
from discord.ext import commands
import json
import hashlib
import random

class ShipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ship", help="Fait un couple entre deux persos de Bleach avec compatibilité.")
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)  # ⏱️ Cooldown utilisateur de 3 secondes
    async def ship(self, ctx):
        try:
            with open("data/bleach_personnages.json", "r", encoding="utf-8") as f:
                persos = json.load(f)

            if len(persos) < 2:
                await ctx.send("❌ Il faut au moins deux personnages dans `bleach_personnages.json`.")
                return

            p1, p2 = random.sample(persos, 2)
            noms_ordonnes = sorted([p1["nom"], p2["nom"]])
            clef = f"{noms_ordonnes[0]}+{noms_ordonnes[1]}"
            hash_bytes = hashlib.md5(clef.encode()).digest()
            score = int.from_bytes(hash_bytes, 'big') % 101

            # 💕 Ajustements selon genre et race
            genre_diff = p1.get("genre") != p2.get("genre")
            races_p1 = set(p1.get("races", []))
            races_p2 = set(p2.get("races", []))
            races_communes = races_p1 & races_p2

            if genre_diff:
                score += 5  # ❤️ Bonus de diversité
            if not races_communes:
                score -= 10  # ⚔️ Malus d’incompatibilité culturelle

            score = max(0, min(score, 100))  # 🔒 Clamp

            # 💬 Résultat
            if score >= 90:
                reaction = "âmes sœurs ! 💞"
            elif score >= 70:
                reaction = "excellente alchimie ! 🔥"
            elif score >= 50:
                reaction = "bonne entente. 😊"
            elif score >= 30:
                reaction = "relation compliquée... 😬"
            else:
                reaction = "aucune chance ! 💔"

            await ctx.send(f"**{p1['nom']}** ❤️ **{p2['nom']}** → Compatibilité : **{score}%** — {reaction}")

        except FileNotFoundError:
            await ctx.send("❌ Fichier `bleach_personnages.json` introuvable.")
        except Exception as e:
            await ctx.send(f"⚠️ Erreur : {e}")

# Chargement automatique
async def setup(bot):
    cog = ShipCommand(bot)
    for command in cog.get_commands():
        command.category = "Fun"
    await bot.add_cog(cog)
