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
from supabase_client import supabase  # Adapter selon ta config supabase

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement du scénario RPG
# ────────────────────────────────────────────────────────────────────────────────
SCENARIO_PATH = os.path.join("data", "rpg_bleach.json")

def load_scenario():
    with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal RPG
# ────────────────────────────────────────────────────────────────────────────────
class RPGBleach(commands.Cog):
    """
    Commande !rpg — Lance une aventure RPG inspirée de Bleach
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

        print(f"[DEBUG] Récupération de la sauvegarde Supabase pour user_id={user_id}")
        data = supabase.table("rpg_save").select("*").eq("user_id", user_id).execute()
        print(f"[DEBUG] Réponse Supabase SELECT: {data}")
        save = data.data[0] if data.data else None

        # Si sauvegarde existante, on récupère infos
        saved_etape = save["etape"] if save else None
        saved_character_name = save["character_name"] if save else None
        saved_mission = save["mission"] if save else None

        intro = self.scenario.get("intro", {})
        intro_texte = intro.get("texte", "Bienvenue dans la Division Z.")
        missions = self.scenario.get("missions", {})
        mission_keys = list(missions.keys())

        emojis = ["✏️"] + ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][:len(mission_keys)]

        embed = discord.Embed(title="🔰 RPG Bleach - Division Z", description=intro_texte, color=discord.Color.teal())
        embed.add_field(name="✏️ Choisir un nom", value="Clique sur ✏️ pour définir le nom de ton personnage.", inline=False)
        for i, key in enumerate(mission_keys):
            m = missions[key]
            embed.add_field(name=f"{emojis[i + 1]} {m['titre']}", value=m["description"], inline=False)

        menu_msg = await ctx.send(embed=embed)
        for emoji in emojis:
            await menu_msg.add_reaction(emoji)

        temp_name = saved_character_name or None

        def check_react(reaction, user):
            return user == ctx.author and reaction.message.id == menu_msg.id and str(reaction.emoji) in emojis

        while True:
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=300, check=check_react)
                print(f"[DEBUG] Réaction reçue: {reaction.emoji} de {ctx.author}")
            except asyncio.TimeoutError:
                await ctx.send("⏰ Tu n’as pas réagi à temps.")
                print("[DEBUG] Timeout sur la réaction")
                return

            if str(reaction.emoji) == "✏️":
                name_prompt = await ctx.send("📛 Réponds à **ce message** avec le nom de ton personnage (5 minutes).")
                print("[DEBUG] Demande du nom envoyée")

                def check_name(m):
                    return m.author == ctx.author and m.reference and m.reference.message_id == name_prompt.id

                try:
                    msg = await self.bot.wait_for("message", timeout=300.0, check=check_name)
                    temp_name = msg.content.strip()
                    await ctx.send(f"✅ Ton nom est enregistré : **{temp_name}**")
                    print(f"[DEBUG] Nom reçu: {temp_name}")
                except asyncio.TimeoutError:
                    await ctx.send("⏰ Temps écoulé pour le nom.")
                    print("[DEBUG] Timeout sur la saisie du nom")
                continue

            if not temp_name:
                await ctx.send("❗ Choisis ton nom avec ✏️ avant de commencer une mission.")
                print("[DEBUG] Tentative de début de mission sans nom défini")
                continue

            # Récupère la mission choisie
            index = emojis.index(str(reaction.emoji)) - 1
            mission_id = mission_keys[index]

            # Si mission + nom = sauvegarde existante, reprendre étape sauvegardée, sinon début mission
            if save and saved_mission == mission_id and saved_character_name == temp_name:
                etape = saved_etape
                print(f"[DEBUG] Reprise sauvegarde mission {mission_id} étape {etape} pour {temp_name}")
            else:
                etape = missions[mission_id]["start"]
                print(f"[DEBUG] Nouvelle partie mission {mission_id} au début étape {etape} pour {temp_name}")

            # Mise à jour sauvegarde (insert ou update)
            response = supabase.table("rpg_save").upsert({
                "user_id": user_id,
                "username": ctx.author.name,
                "character_name": temp_name,
                "mission": mission_id,
                "etape": etape
            }, on_conflict=["user_id"]).execute()
            print(f"[DEBUG] Réponse Supabase UPSERT: {response}")

            await self.jouer_etape(ctx, etape, temp_name, mission_id)
            return

    async def jouer_etape(self, ctx: commands.Context, etape_id: str, character_name: str, mission_id: str):
        etape = self.scenario.get(etape_id)
        if not etape:
            await ctx.send("❌ Étape du scénario introuvable.")
            print(f"[DEBUG] Étape introuvable: {etape_id}")
            return

        texte = etape["texte"].replace("{nom}", character_name)
        embed = discord.Embed(
            title=f"🧭 Mission : {self.scenario['missions'][mission_id]['titre']}",
            description=texte,
            color=discord.Color.dark_purple()
        )

        emojis = []
        for choix in etape.get("choix", []):
            embed.add_field(name=choix["emoji"], value=choix["texte"], inline=False)
            emojis.append(choix["emoji"])

        message = await ctx.send(embed=embed)
        for emoji in emojis:
            await message.add_reaction(emoji)

        def check_choice(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in emojis

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=300.0, check=check_choice)
            print(f"[DEBUG] Choix reçu: {reaction.emoji} de {ctx.author}")
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tu n’as pas réagi à temps.")
            print("[DEBUG] Timeout sur choix de l'étape")
            return

        for choix in etape["choix"]:
            if choix["emoji"] == str(reaction.emoji):
                next_etape = choix["suivant"]
                print(f"[DEBUG] Sauvegarde étape suivante user_id={ctx.author.id}, étape={next_etape}")
                response = supabase.table("rpg_save").upsert({
                    "user_id": str(ctx.author.id),
                    "username": ctx.author.name,
                    "character_name": character_name,
                    "mission": mission_id,
                    "etape": next_etape
                }, on_conflict=["user_id"]).execute()
                print(f"[DEBUG] Réponse Supabase UPSERT étape suivante: {response}")

                await self.jouer_etape(ctx, next_etape, character_name, mission_id)
                return

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = RPGBleach(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)
