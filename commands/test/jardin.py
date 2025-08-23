# ────────────────────────────────────────────────────────────────────────────────
# 📌 jardin.py — Commande interactive /jardin et !jardin
# Objectif : Chaque utilisateur a un jardin persistant avec des fleurs
# Catégorie : Jeu
# Accès : Tout le monde
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord import app_commands
from discord.ext import commands
import os
from utils.discord_utils import safe_send, safe_respond  # ✅
from supabase import create_client, Client

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Connexion Supabase
# ────────────────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "gardens"

# ────────────────────────────────────────────────────────────────────────────────
# 🌱 Constantes du jeu
# ────────────────────────────────────────────────────────────────────────────────
DEFAULT_GARDEN = {
    "line1": "🌱🌱🌱🌱🌱🌱🌱🌱",
    "line2": "🌱🌱🌱🌱🌱🌱🌱🌱",
    "line3": "🌱🌱🌱🌱🌱🌱🌱🌱",
    "tulipes": 0,
    "roses": 0,
    "jacinthes": 0,
    "hibiscus": 0,
    "paquerettes": 0,
    "tournesols": 0,
    "argent": 0,
    "armee": "🐐"
}

FLEUR_EMOJIS = {
    "tulipes": "🌷",
    "roses": "🌹",
    "jacinthes": "🪻",
    "hibiscus": "🌺",
    "paquerettes": "🌼",
    "tournesols": "🌻"
}

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Fonctions utilitaires
# ────────────────────────────────────────────────────────────────────────────────
async def get_or_create_garden(user_id: int, username: str):
    """Récupère le jardin de l'utilisateur ou le crée s'il n'existe pas."""
    res = supabase.table(TABLE_NAME).select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]

    new_garden = {"user_id": user_id, "username": username, **DEFAULT_GARDEN}
    supabase.table(TABLE_NAME).insert(new_garden).execute()
    return new_garden

def build_garden_embed(garden: dict) -> discord.Embed:
    """Construit un embed avec le jardin et l'inventaire."""
    lines = [garden["line1"], garden["line2"], garden["line3"]]
    inv = " / ".join(
        f"{FLEUR_EMOJIS[f]}{garden[f]}" for f in FLEUR_EMOJIS
    )

    embed = discord.Embed(
        title=f"🏡 Jardin de {garden['username']}",
        description="\n".join(lines) + f"\n\n{inv}",
        color=discord.Color.green()
    )
    embed.add_field(name="Armée", value=garden["armee"], inline=True)
    embed.add_field(name="Argent", value=f"{garden['argent']} 💰", inline=True)
    return embed

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Boutons d’action
# ────────────────────────────────────────────────────────────────────────────────
class JardinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Engrais", emoji="💩", style=discord.ButtonStyle.green)
    async def engrais(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💩 Fonction engrais pas encore implémentée !", ephemeral=True)

    @discord.ui.button(label="Couper", emoji="✂️", style=discord.ButtonStyle.red)
    async def couper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✂️ Fonction couper pas encore implémentée !", ephemeral=True)

    @discord.ui.button(label="Bourse", emoji="💶", style=discord.ButtonStyle.blurple)
    async def bourse(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💶 Fonction bourse pas encore implémentée !", ephemeral=True)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Jardin(commands.Cog):
    """Commande /jardin et !jardin — Voir son jardin"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="jardin", description="Affiche ton jardin personnel 🌱")
    async def slash_jardin(self, interaction: discord.Interaction):
        try:
            garden = await get_or_create_garden(interaction.user.id, interaction.user.name)
            embed = build_garden_embed(garden)
            view = JardinView()
            await safe_respond(interaction, embed=embed, view=view)
        except Exception as e:
            print(f"[ERREUR /jardin] {e}")
            await safe_respond(interaction, "❌ Une erreur est survenue.", ephemeral=True)

    @commands.command(name="jardin")
    async def prefix_jardin(self, ctx: commands.Context):
        try:
            garden = await get_or_create_garden(ctx.author.id, ctx.author.name)
            embed = build_garden_embed(garden)
            view = JardinView()
            await safe_send(ctx.channel, embed=embed, view=view)
        except Exception as e:
            print(f"[ERREUR !jardin] {e}")
            await safe_send(ctx.channel, "❌ Une erreur est survenue.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Jardin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)



