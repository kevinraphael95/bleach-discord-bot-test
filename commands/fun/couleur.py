# ────────────────────────────────────────────────────────────────
#        🎨 COMMANDE DISCORD - COULEUR ALÉATOIRE       
# ────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import random
import discord
from discord.ext import commands

# ────────────────────────────────────────────────────────────────═
# 📦 Classe principale de la commande "couleur"
# ────────────────────────────────────────────────────────────────═
class CouleurCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ───────────────────────────────────────────────
    # 🎯 Commande !couleur : génère une couleur unique
    # Cooldown : 1 fois toutes les 3 secondes par utilisateur
    # ───────────────────────────────────────────────
    @commands.command(
        name="couleur",
        help="🎨 Affiche une couleur aléatoire avec ses codes HEX et RGB."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def couleur(self, ctx):
        # ─────────────────────────────
        # 🎲 Génération d'un code HEX
        # ─────────────────────────────
        code_hex = random.randint(0, 0xFFFFFF)
        hex_str = f"#{code_hex:06X}"  # Ex: #1A2B3C

        # ─────────────────────────────
        # 🌈 Conversion HEX ➜ RGB
        # ─────────────────────────────
        r = (code_hex >> 16) & 0xFF
        g = (code_hex >> 8) & 0xFF
        b = code_hex & 0xFF
        rgb_str = f"({r}, {g}, {b})"

        # ─────────────────────────────
        # 🖼️ Génération d'une image couleur
        # ─────────────────────────────
        image_url = f"https://dummyimage.com/700x200/{code_hex:06x}/{code_hex:06x}.png&text=+"

        # ─────────────────────────────
        # 📋 Création de l'embed Discord
        # ─────────────────────────────
        embed = discord.Embed(
            title="🌈 Couleur aléatoire",
            description=(
                f"🔹 **Code HEX** : `{hex_str}`\n"
                f"🔸 **Code RGB** : `{rgb_str}`"
            ),
            color=code_hex
        )

        # 🌄 Ajout de l'image dans l'embed
        embed.set_image(url=image_url)

        # 🖊️ Ajout d'une signature
        embed.set_footer(
            text="💡 Utilise !couleur pour découvrir une autre teinte magique.",
            icon_url="https://cdn-icons-png.flaticon.com/512/616/616408.png"
        )

        # ⏰ Timestamp pour la beauté
        embed.timestamp = ctx.message.created_at

        # 📤 Envoie de l'embed dans le salon
        await ctx.send(embed=embed)

# ────────────────────────────────────────────────────────────────═
# 🔌 Fonction de setup pour charger le Cog
# ────────────────────────────────────────────────────────────────═
async def setup(bot):
    cog = CouleurCommand(bot)
    for command in cog.get_commands():
        command.category = "Fun"  # 📁 Classement dans la catégorie "Fun"
    await bot.add_cog(cog)
