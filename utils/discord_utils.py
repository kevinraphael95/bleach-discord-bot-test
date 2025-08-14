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

# File d'attente globale pour éviter les rafales
_request_lock = asyncio.Lock()
_last_delay = 0  # backoff progressif

async def _handle_rate_limit(e: HTTPException):
    """
    Gère le rate-limit Discord et Cloudflare de façon robuste.
    """
    global _last_delay

    if e.status == 429:
        # Discord rate limit
        retry_after = getattr(e, "retry_after", None)
        delay = retry_after if retry_after else 10
        print(f"[RateLimit] Discord → pause {delay:.1f}s")
        await asyncio.sleep(delay)
        _last_delay = min(_last_delay + 1, 60)  # backoff progressif max 1min
    elif e.status == 1015:
        # Cloudflare ban temporaire
        print("[Cloudflare] Erreur 1015 → Ban temporaire, pause 60s")
        await asyncio.sleep(60)
        _last_delay = min(_last_delay + 10, 300)  # backoff progressif max 5min
    else:
        raise e


async def _execute_safely(coro):
    """
    Exécute une requête Discord en gérant les rate-limits et Cloudflare.
    """
    async with _request_lock:  # évite plusieurs appels en même temps
        if _last_delay > 0:
            print(f"[AntiFlood] Pause {_last_delay}s avant requête")
            await asyncio.sleep(_last_delay)
        try:
            return await coro
        except HTTPException as e:
            await _handle_rate_limit(e)
            return await coro


# ────────────────────────────────────────────────────────────────────────────────
# 🛡️ Fonctions sécurisées
# ────────────────────────────────────────────────────────────────────────────────

async def safe_send(channel: discord.TextChannel, content=None, **kwargs):
    return await _execute_safely(channel.send(content=content, **kwargs))

async def safe_edit(message: discord.Message, content=None, **kwargs):
    return await _execute_safely(message.edit(content=content, **kwargs))

async def safe_respond(interaction: discord.Interaction, content=None, **kwargs):
    return await _execute_safely(interaction.response.send_message(content=content, **kwargs))

async def safe_reply(ctx_or_message, content=None, **kwargs):
    return await _execute_safely(ctx_or_message.reply(content=content, **kwargs))

async def safe_add_reaction(message: discord.Message, emoji: str, delay: float = 0.3):
    await _execute_safely(message.add_reaction(emoji))
    await asyncio.sleep(delay)  # petit cooldown anti-429

async def safe_followup(interaction: discord.Interaction, content=None, **kwargs):
    return await _execute_safely(interaction.followup.send(content=content, **kwargs))

async def safe_delete(message: discord.Message, delay: float = 0):
    await _execute_safely(message.delete(delay=delay))

async def safe_clear_reactions(message: discord.Message):
    await _execute_safely(message.clear_reactions())
