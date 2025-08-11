# ────────────────────────────────────────────────────────────────────────────────#
# 📌 react.py — Commande interactive /react et !react
# Objectif : Réagit à un message avec un emoji animé temporaire (3 minutes)
# Catégorie : Général
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────#

# ────────────────────────────────────────────────────────────────────────────────#
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────#
import discord
from discord import app_commands
from discord.ext import commands
from utils.discord_utils import safe_send
import asyncio

# ────────────────────────────────────────────────────────────────────────────────#
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────#
class ReactCommand(commands.Cog):
    """
    Commande /react et !react — Réagit à un message avec un emoji animé, puis le retire
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────────────────────#
    # 🔹 Fonction interne commune pour exécuter la logique principale
    # ────────────────────────────────────────────────────────────────────────────#
    async def _react_to_message(self, channel: discord.abc.Messageable, guild: discord.Guild, 
                                emoji_name: str, reference_message_id: int = None, 
                                before_time=None, bot_member=None):
        """Réagit temporairement à un message (référencé ou dernier avant commande)."""

        emoji_name_cleaned = emoji_name.strip(":").lower()

        # Recherche de l'emoji animé sur le serveur
        emoji = next((e for e in guild.emojis if e.animated and e.name.lower() == emoji_name_cleaned), None)
        if not emoji:
            await safe_send(channel, f"❌ Emoji animé `:{emoji_name_cleaned}:` introuvable sur ce serveur.", delete_after=5)
            return

        target_message = None
        try:
            if reference_message_id:
                # Récupère le message référencé
                target_message = await channel.fetch_message(reference_message_id)
            else:
                # Sinon, récupère le dernier message avant le temps donné
                async for msg in channel.history(limit=20, before=before_time):
                    target_message = msg
                    break

            if not target_message:
                await safe_send(channel, "❌ Aucun message valide à réagir.", delete_after=5)
                return

            # Ajoute la réaction
            await target_message.add_reaction(emoji)
            print(f"✅ Réaction {emoji} ajoutée à {target_message.id}")

            # Attend 3 minutes
            await asyncio.sleep(180)

            # Retire la réaction ajoutée par le bot
            await target_message.remove_reaction(emoji, bot_member)
            print(f"🔁 Réaction {emoji} retirée de {target_message.id}")

        except discord.NotFound:
            await safe_send(channel, "❌ Message référencé introuvable.", delete_after=5)
        except Exception as e:
            print(f"⚠️ Erreur lors de la réaction : {e}")

    # ────────────────────────────────────────────────────────────────────────────#
    # 🔹 Commande SLASH
    # ────────────────────────────────────────────────────────────────────────────#
    @app_commands.command(
        name="react",
        description="Réagit temporairement avec un emoji animé à un message (répondre ou dernier)."
    )
    @app_commands.describe(emoji="Nom de l'emoji animé du serveur (sans :)")
    async def slash_react(self, interaction: discord.Interaction, emoji: str):
        """Commande slash principale /react"""
        await interaction.response.defer(ephemeral=True)
        try:
            await self._react_to_message(
                channel=interaction.channel,
                guild=interaction.guild,
                emoji_name=emoji,
                reference_message_id=interaction.message.reference.message_id if interaction.message and interaction.message.reference else None,
                before_time=interaction.message.created_at if interaction.message else None,
                bot_member=interaction.guild.me,
            )
            await interaction.followup.send("✅ Réaction ajoutée temporairement.", ephemeral=True)
        except Exception as e:
            print(f"[ERREUR /react] {e}")
            await interaction.followup.send("❌ Une erreur est survenue.", ephemeral=True)

    # ────────────────────────────────────────────────────────────────────────────#
    # 🔹 Commande PREFIX
    # ────────────────────────────────────────────────────────────────────────────#
    @commands.command(
        name="react",
        aliases=["r"],
        help="Réagit à un message avec un emoji animé, puis le retire après 3 minutes."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def prefix_react(self, ctx: commands.Context, emoji_name: str):
        """Commande préfixe principale !react"""
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass  # Ignore si suppression impossible

        await self._react_to_message(
            channel=ctx.channel,
            guild=ctx.guild,
            emoji_name=emoji_name,
            reference_message_id=ctx.message.reference.message_id if ctx.message.reference else None,
            before_time=ctx.message.created_at,
            bot_member=ctx.guild.me,
        )

# ────────────────────────────────────────────────────────────────────────────────#
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────#
async def setup(bot: commands.Bot):
    cog = ReactCommand(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Général"
    await bot.add_cog(cog)
