# ────────────────────────────────────────────────────────────────────────────────
# 📌 discord_utils.py — Fonctions utilitaires avec gestion du rate-limit
# Objectif : Fournir des fonctions sécurisées pour send/edit/respond Discord et API externes
# Catégorie : Général
# Accès : Public (utilisable dans tous les Cogs)
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import asyncio
import discord
import aiohttp
from discord.errors import HTTPException
from aiohttp import ClientResponseError

# File d'attente globale pour éviter les rafales
_request_lock = asyncio.Lock()
_last_delay = 0  # backoff progressif

# ────────────────────────────────────────────────────────────────────────────────
# 🛡️ Gestion du rate-limit
# ────────────────────────────────────────────────────────────────────────────────
async def _handle_rate_limit(e):
    """
    Gère le rate-limit Discord et Cloudflare de façon robuste.
    """
    global _last_delay

    if isinstance(e, HTTPException):
        # Discord
        if e.status == 429:
            retry_after = getattr(e, "retry_after", None)
            delay = retry_after if retry_after else 10
            print(f"[RateLimit] Discord → pause {delay:.1f}s")
            await asyncio.sleep(delay)
            _last_delay = min(_last_delay + 1, 60)
        elif e.status == 1015:
            print("[Cloudflare] Erreur 1015 → Ban temporaire, pause 60s")
            await asyncio.sleep(60)
            _last_delay = min(_last_delay + 10, 300)
        else:
            raise e

    elif isinstance(e, ClientResponseError):
        # API externe
        if e.status == 429:
            print(f"[RateLimit API] Pause 10s")
            await asyncio.sleep(10)
            _last_delay = min(_last_delay + 1, 60)
        elif e.status == 1015:
            print("[Cloudflare API] Erreur 1015 → Ban temporaire, pause 60s")
            await asyncio.sleep(60)
            _last_delay = min(_last_delay + 10, 300)
        else:
            raise e

    else:
        raise e


async def _execute_safely(coro):
    """
    Exécute une requête Discord en gérant les rate-limits et Cloudflare.
    """
    async with _request_lock:
        if _last_delay > 0:
            print(f"[AntiFlood] Pause {_last_delay}s avant requête")
            await asyncio.sleep(_last_delay)
        try:
            return await coro
        except (HTTPException, ClientResponseError) as e:
            await _handle_rate_limit(e)
            return await coro


# ────────────────────────────────────────────────────────────────────────────────
# 🌐 Safe request (API externes)
# ────────────────────────────────────────────────────────────────────────────────
async def safe_request(method: str, url: str, **kwargs):
    """
    Effectue une requête HTTP avec gestion des rate-limits et Cloudflare (API externes).
    Utilisation :
        data = await safe_request("GET", "https://api.exemple.com/data")
    """
    async with _request_lock:
        if _last_delay > 0:
            print(f"[AntiFlood API] Pause {_last_delay}s avant requête API")
            await asyncio.sleep(_last_delay)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except ClientResponseError as e:
            await _handle_rate_limit(e)
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as resp:
                    resp.raise_for_status()
                    return await resp.json()


# ────────────────────────────────────────────────────────────────────────────────
# 🛡️ Fonctions sécurisées Discord
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
    await asyncio.sleep(delay)

async def safe_followup(interaction: discord.Interaction, content=None, **kwargs):
    return await _execute_safely(interaction.followup.send(content=content, **kwargs))

async def safe_delete(message: discord.Message, delay: float = 0):
    await _execute_safely(message.delete(delay=delay))

async def safe_clear_reactions(message: discord.Message):
    await _execute_safely(message.clear_reactions())
