# ────────────────────────────────────────────────────────────────────────────────
# 📌 rpg_bleach.py — Commande interactive !rpg
# Objectif : Commencer et jouer un RPG textuel inspiré de Bleach avec sauvegarde Supabase
# Catégorie : VAACT
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import asyncio
import json
import os
from utils.supabase_client import supabase
from utils.discord_utils import safe_send, safe_edit, safe_add_reaction, safe_clear_reactions  # ajout safe_clear_reactions

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Constantes et configuration
# ────────────────────────────────────────────────────────────────────────────────
SCENARIO_PATH = os.path.join("data", "rpg_bleach.json")

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement du scénario RPG
# ────────────────────────────────────────────────────────────────────────────────
def load_scenario():
    with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal RPG
# ────────────────────────────────────────────────────────────────────────────────
class RPGBleach(commands.Cog):
    """
    🎮 Commande !rpg — Lance une aventure RPG inspirée de Bleach avec sauvegarde Supabase.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scenario = load_scenario()

    @commands.command(
        name="rpg",
        help="Commence ton aventure dans la Division Z à Karakura.",
        description="Lance une aventure interactive avec choix et sauvegarde."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def rpg(self, ctx: commands.Context):
        user_id = str(ctx.author.id)

        print(f"[DEBUG] Chargement sauvegarde Supabase pour {user_id}")
        response = supabase.table("rpg_save").select("*").eq("user_id", user_id).execute()
        save = response.data[0] if response.data else None

        saved_etape = save["etape"] if save else None
        saved_name = save["character_name"] if save else None
        saved_mission = save["mission"] if save else None

        intro = self.scenario.get("intro", {})
        intro_texte = intro.get("texte", "Bienvenue dans la Division Z.")
        missions = self.scenario.get("missions", {})
        mission_ids = list(missions.keys())

        emojis = ["✏️"] + ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][:len(mission_ids)]

        embed = discord.Embed(
            title="🔰 RPG Bleach - Division Z",
            description=intro_texte,
            color=discord.Color.teal()
        )
        embed.add_field(name="✏️ Choisir un nom", value="Clique sur ✏️ pour définir le nom de ton personnage.", inline=False)
        for i, key in enumerate(mission_ids):
            mission = missions[key]
            embed.add_field(name=f"{emojis[i + 1]} {mission['titre']}", value=mission["description"], inline=False)

        menu = await safe_send(ctx, embed=embed)
        for emoji in emojis:
            await safe_add_reaction(menu, emoji)

        temp_name = saved_name or None

        def check_react(reaction, user):
            return user == ctx.author and reaction.message.id == menu.id and str(reaction.emoji) in emojis

        while True:
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=300, check=check_react)
            except asyncio.TimeoutError:
                await safe_send(ctx, content="⏰ Tu n’as pas réagi à temps.")
                return

            emoji = str(reaction.emoji)

            # Enlever la réaction utilisateur pour garder l'interface propre
            try:
                await menu.remove_reaction(emoji, ctx.author)
            except:
                pass  # Ignore erreur si pas possible (permissions)

            if emoji == "✏️":
                prompt = await safe_send(ctx, content="📛 Réponds à **ce message** avec le nom de ton personnage (5 minutes).")

                def check_msg(m):
                    return m.author == ctx.author and m.reference and m.reference.message_id == prompt.id

                try:
                    msg = await self.bot.wait_for("message", timeout=300, check=check_msg)
                    temp_name = msg.content.strip()
                    await safe_send(ctx, content=f"✅ Ton nom est enregistré : **{temp_name}**")
                except asyncio.TimeoutError:
                    await safe_send(ctx, content="⏰ Temps écoulé pour entrer ton nom.")
                continue

            if not temp_name:
                await safe_send(ctx, content="❗ Choisis ton nom avant de commencer une mission.")
                continue

            mission_index = emojis.index(emoji) - 1
            mission_id = mission_ids[mission_index]

            if save and saved_mission == mission_id and saved_name == temp_name:
                etape_id = saved_etape
            else:
                etape_id = missions[mission_id]["start"]

            upsert = supabase.table("rpg_save").upsert({
                "user_id": user_id,
                "username": ctx.author.name,
                "character_name": temp_name,
                "mission": mission_id,
                "etape": etape_id
            }, on_conflict=["user_id"]).execute()

            if not upsert.data:
                await safe_send(ctx, content="⚠️ Erreur lors de la sauvegarde.")
                return

            await self.jouer_etape(ctx, etape_id, temp_name, mission_id, menu)
            return

    async def jouer_etape(self, ctx: commands.Context, etape_id: str, nom: str, mission_id: str, msg: discord.Message):
        etape = self.scenario.get(etape_id)
        if not etape:
            await safe_send(ctx, content="❌ Étape introuvable.")
            return

        while True:
            texte = etape["texte"].replace("{nom}", nom)
            embed = discord.Embed(
                title=f"🧭 Mission : {self.scenario['missions'][mission_id]['titre']}",
                description=texte,
                color=discord.Color.dark_purple()
            )

            emojis = []
            for choix in etape.get("choix", []):
                embed.add_field(name=choix["emoji"], value=choix["texte"], inline=False)
                emojis.append(choix["emoji"])

            # Edit le même message avec le nouvel embed
            await safe_edit(msg, embed=embed)

            # Clear les réactions précédentes
            try:
                await msg.clear_reactions()
            except:
                pass

            # Ajouter les réactions pour les choix
            for emoji in emojis:
                await safe_add_reaction(msg, emoji)

            def check_choix(r, u):
                return u == ctx.author and r.message.id == msg.id and str(r.emoji) in emojis

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=300, check=check_choix)
            except asyncio.TimeoutError:
                await safe_send(ctx, content="⏰ Tu n’as pas réagi à temps.")
                return

            selected = str(reaction.emoji)

            # Retirer la réaction de l'utilisateur pour garder propre
            try:
                await msg.remove_reaction(selected, ctx.author)
            except:
                pass

            # Trouver la prochaine étape correspondant au choix
            next_etape = None
            for choix in etape["choix"]:
                if choix["emoji"] == selected:
                    next_etape = choix["suivant"]
                    break

            if next_etape is None:
                await safe_send(ctx, content="❌ Choix invalide.")
                return

            # Sauvegarde mise à jour
            response = supabase.table("rpg_save").upsert({
                "user_id": str(ctx.author.id),
                "username": ctx.author.name,
                "character_name": nom,
                "mission": mission_id,
                "etape": next_etape
            }, on_conflict=["user_id"]).execute()

            if not response.data:
                await safe_send(ctx, content="⚠️ Erreur lors de la sauvegarde.")
                return

            # Charge la prochaine étape pour la boucle
            etape_id = next_etape
            etape = self.scenario.get(etape_id)
            if not etape:
                await safe_send(ctx, content="🎉 Fin de la mission ou étape inconnue.")
                return

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = RPGBleach(bot)
    for command in cog.get_commands():
        command.category = "Test"
    await bot.add_cog(cog)
