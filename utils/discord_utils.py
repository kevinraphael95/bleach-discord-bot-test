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
# 🛡️ Fonctions sécurisées pour Discord
# ────────────────────────────────────────────────────────────────────────────────

async def safe_send(channel: discord.TextChannel, content=None, **kwargs):
    """
    Envoie un message sur un channel Discord avec gestion du rate-limit (429).
    """
    try:
        return await channel.send(content=content, **kwargs)
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_send() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            return await channel.send(content=content, **kwargs)
        raise e

async def safe_edit(message: discord.Message, content=None, **kwargs):
    """
    Modifie un message Discord avec gestion du rate-limit (429).
    """
    try:
        return await message.edit(content=content, **kwargs)
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_edit() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            return await message.edit(content=content, **kwargs)
        raise e

async def safe_respond(interaction: discord.Interaction, content=None, **kwargs):
    """
    Répond à une interaction avec gestion du rate-limit (429).
    """
    try:
        return await interaction.response.send_message(content=content, **kwargs)
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_respond() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            return await interaction.response.send_message(content=content, **kwargs)
        raise e

async def safe_reply(ctx_or_message, content=None, **kwargs):
    """
    Répond à un message ou un contexte Discord avec gestion du rate-limit (429).
    """
    try:
        return await ctx_or_message.reply(content=content, **kwargs)
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_reply() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            return await ctx_or_message.reply(content=content, **kwargs)
        raise e

async def safe_add_reaction(message: discord.Message, emoji: str, delay: float = 0.3):
    """
    Ajoute une réaction en toute sécurité avec gestion du rate-limit (429).
    Un petit délai est ajouté entre chaque réaction.
    """
    try:
        await message.add_reaction(emoji)
        await asyncio.sleep(delay)  # anti-429 : petit cooldown
    except HTTPException as e:
        if e.status == 429:
            print(f"[RateLimit] safe_add_reaction() → 429 sur {emoji}. Pause...")
            await asyncio.sleep(10)
            await message.add_reaction(emoji)
            await asyncio.sleep(delay)
        else:
            raise e
    except Exception as e:
        print(f"[Erreur] safe_add_reaction() → {e}")



async def safe_followup(interaction: discord.Interaction, content=None, **kwargs):
    """
    Envoie un message de suivi avec gestion du rate-limit (429).
    """
    try:
        return await interaction.followup.send(content=content, **kwargs)
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_followup() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            return await interaction.followup.send(content=content, **kwargs)
        raise e

async def safe_delete(message: discord.Message, delay: float = 0):
    """
    Supprime un message Discord avec gestion du rate-limit (429).
    """
    try:
        await message.delete(delay=delay)
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_delete() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            await message.delete(delay=delay)
        else:
            raise e
    except Exception as e:
        print(f"[Erreur] safe_delete() → {e}")

async def safe_clear_reactions(message: discord.Message):
    """
    Supprime toutes les réactions d’un message avec gestion du rate-limit (429).
    """
    try:
        await message.clear_reactions()
    except HTTPException as e:
        if e.status == 429:
            print("[RateLimit] safe_clear_reactions() → 429 Too Many Requests. Pause...")
            await asyncio.sleep(10)
            await message.clear_reactions()
        else:
            raise e
    except Exception as e:
        print(f"[Erreur] safe_clear_reactions() → {e}")

