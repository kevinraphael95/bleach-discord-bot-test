# ────────────────────────────────────────────────────────────────────────────────
# 📌 discord_utils.py — Fonctions utilitaires avec gestion du rate-limit
# Objectif : Fournir des fonctions sécurisées pour send/edit/respond Discord
# Catégorie : Général
# Accès : Public (utilisable dans tous les Cogs)
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import asyncio
import discord
from discord.errors import HTTPException

# ────────────────────────────────────────────────────────────────────────────────
# 🔹 Queue globale pour toutes les requêtes Discord
# ────────────────────────────────────────────────────────────────────────────────
discord_queue = asyncio.Queue()
RATE_LIMIT_DELAY = 1.0  # délai minimal entre chaque requête (en secondes)
COOLDOWN_429 = 10       # pause en cas de 429

# ────────────────────────────────────────────────────────────────────────────────
# 🔹 Worker qui exécute les actions de la queue
# ────────────────────────────────────────────────────────────────────────────────
async def discord_worker():
    while True:
        func, args, kwargs, fut = await discord_queue.get()
        try:
            result = await func(*args, **kwargs)
            fut.set_result(result)
        except HTTPException as e:
            if e.status == 429:
                print("[RateLimit] 429 détecté, pause globale...")
                await asyncio.sleep(COOLDOWN_429)
                try:
                    result = await func(*args, **kwargs)
                    fut.set_result(result)
                except Exception as e2:
                    fut.set_exception(e2)
            else:
                fut.set_exception(e)
        except Exception as e:
            fut.set_exception(e)
        await asyncio.sleep(RATE_LIMIT_DELAY)
        discord_queue.task_done()

# ❌ PLUS DE create_task ici au niveau global
# Tu devras lancer le worker depuis ton bot.py comme ceci :
# asyncio.create_task(discord_utils.discord_worker())

# ────────────────────────────────────────────────────────────────────────────────
# 🔹 Fonction pour ajouter une action à la queue
# ────────────────────────────────────────────────────────────────────────────────
def enqueue(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    discord_queue.put_nowait((func, args, kwargs, fut))
    return fut

# ────────────────────────────────────────────────────────────────────────────────
# 🔹 Fonctions “safe” qui utilisent la queue globale
# ────────────────────────────────────────────────────────────────────────────────
async def safe_send(channel: discord.TextChannel, content=None, **kwargs):
    return await enqueue(channel.send, content=content, **kwargs)

async def safe_edit(message: discord.Message, content=None, **kwargs):
    return await enqueue(message.edit, content=content, **kwargs)

async def safe_respond(interaction: discord.Interaction, content=None, **kwargs):
    return await enqueue(interaction.response.send_message, content=content, **kwargs)

async def safe_followup(interaction: discord.Interaction, content=None, **kwargs):
    return await enqueue(interaction.followup.send, content=content, **kwargs)

async def safe_reply(ctx_or_message, content=None, **kwargs):
    return await enqueue(ctx_or_message.reply, content=content, **kwargs)

async def safe_add_reaction(message: discord.Message, emoji: str):
    return await enqueue(message.add_reaction, emoji)

async def safe_delete(message: discord.Message, delay: float = 0):
    return await enqueue(message.delete, delay=delay)

async def safe_clear_reactions(message: discord.Message):
    return await enqueue(message.clear_reactions)
