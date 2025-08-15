# ────────────────────────────────────────────────────────────────────────────────
# 📌 bot.py — Script principal du bot Discord
# Objectif : Initialisation, gestion des commandes et événements du bot
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 🟢 Serveur Keep-Alive (Render)
# ──────────────────────────────────────────────────────────────
from tasks.keep_alive import keep_alive

# ──────────────────────────────────────────────────────────────
# 📦 Modules standards
# ──────────────────────────────────────────────────────────────
import os
import json
import uuid
import asyncio
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────
# 📦 Modules tiers
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────
# 📦 Modules internes
# ──────────────────────────────────────────────────────────────
from supabase_client import supabase
from utils.discord_utils import safe_call, safe_send, safe_edit, safe_respond, safe_followup, safe_add_reaction

# ──────────────────────────────────────────────────────────────
# 🔧 Initialisation de l’environnement
# ──────────────────────────────────────────────────────────────

os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
INSTANCE_ID = str(uuid.uuid4())

with open("instance_id.txt", "w") as f:
    f.write(INSTANCE_ID)

def get_prefix(bot, message):
    return COMMAND_PREFIX

# ──────────────────────────────────────────────────────────────
# ⚙️ Intents & Création du bot
# ──────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)
bot.is_main_instance = False
bot.INSTANCE_ID = INSTANCE_ID
bot.supabase = supabase

# ──────────────────────────────────────────────────────────────
# 📁 Chargement des réponses JSON
# ──────────────────────────────────────────────────────────────

with open("data/reponses.json", encoding="utf-8") as f:
    REPONSES = json.load(f)

GIFS_FOLDER = "data/gifs"

# ──────────────────────────────────────────────────────────────
# 🔌 Chargement dynamique des commandes
# ──────────────────────────────────────────────────────────────

async def load_commands():
    for root, dirs, files in os.walk("commands"):
        for file in files:
            if file.endswith(".py"):
                relative_path = os.path.relpath(os.path.join(root, file), ".")
                module_path = relative_path.replace(os.path.sep, ".").replace(".py", "")
                try:
                    if module_path in bot.extensions:
                        await bot.unload_extension(module_path)
                    await bot.load_extension(module_path)
                    print(f"✅ Loaded {module_path}")
                except Exception as e:
                    print(f"❌ Failed to load {module_path}: {e}")

    try:
        await bot.load_extension("tasks.heartbeat")
        print("✅ Loaded tasks.heartbeat")
    except Exception as e:
        print(f"❌ Failed to load tasks.heartbeat: {e}")

# ──────────────────────────────────────────────────────────────
# 🔔 Événement on_ready : présence + verrouillage
# ──────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")
    await safe_call(bot.change_presence, activity=discord.Activity(type=discord.ActivityType.watching, name="Bleach"))

    now = datetime.now(timezone.utc).isoformat()

    try:
        print("💣 Suppression de tout verrou précédent...")
        supabase.table("bot_lock").delete().eq("id", "reiatsu_lock").execute()

        print(f"🔐 Prise de verrou par cette instance : {INSTANCE_ID}")
        supabase.table("bot_lock").insert({
            "id": "reiatsu_lock",
            "instance_id": INSTANCE_ID,
            "updated_at": now
        }).execute()

        bot.is_main_instance = True
        print(f"✅ Instance principale active : {INSTANCE_ID}")

        # Chargement du spawner Reiatsu
        await bot.load_extension("tasks.reiatsu_spawner")
        print("✅ Spawner Reiatsu chargé.")
        
        # synchronisation des commandes slash
        await bot.tree.sync()
        print("✅ Slash commands synchronisées")
    except Exception as e:
        print(f"⚠️ Impossible de se connecter à Supabase : {e}")
        print("🔓 Aucune gestion de verrou — le bot démarre quand même.")

# ──────────────────────────────────────────────────────────────
# 📩 Événement on_message : gestion du verrou + commandes
# ──────────────────────────────────────────────────────────────

@bot.event
async def on_message(message):
    try:
        lock = supabase.table("bot_lock").select("instance_id").eq("id", "reiatsu_lock").execute()
        if lock.data and lock.data[0]["instance_id"] != INSTANCE_ID:
            return
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification du verrou Supabase : {e}")

    if message.author.bot:
        return

    prefix = get_prefix(bot, message)

    if message.content.strip() == f"<@{bot.user.id}>" or message.content.strip() == f"<@!{bot.user.id}>":
        await safe_send(message.channel, f"👋 Salut {message.author.mention} ! Utilise `{prefix}help` pour voir mes commandes.")
        return

    if not message.content.startswith(prefix):
        return

    await bot.process_commands(message)

# ──────────────────────────────────────────────────────────────
# 🚀 Lancement du bot
# ──────────────────────────────────────────────────────────────

async def main():
    asyncio.create_task(discord_worker())  # démarre le worker avant tout
    await load_commands()
    await bot.start(TOKEN)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
