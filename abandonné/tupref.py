# ────────────────────────────────────────────────────────────────────────────────
# 📌 bleach_votes.py — Commandes interactives de vote sur personnages Bleach
# Objectif : Commandes fun pour voter, voir le top et réinitialiser les votes
# Catégorie : Bleach
# Accès : Public / Admin (reset)
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import json
import random
from supabase_client import supabase  # ton client Supabase
# Import des fonctions sécurisées pour éviter le rate-limit 429
from utils.discord_utils import safe_send  # fonctions utils avec gestion 429

# ────────────────────────────────────────────────────────────────────────────────
# 🤔 TU PRÉFÈRES QUI ? - COMMANDE DE VOTE FUN & IMMERSIVE
# ────────────────────────────────────────────────────────────────────────────────
class TuPrefCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tupref",
        aliases=["tp"],
        help="🤔 Choisis ton personnage préféré entre deux propositions aléatoires."
    )
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.user)
    async def tupref(self, ctx: commands.Context):
        try:
            with open("data/bleach_personnages.json", "r", encoding="utf-8") as f:
                persos = json.load(f)

            if len(persos) < 2:
                await safe_send(ctx.channel, "❌ Il faut au moins deux personnages pour lancer un vote.")
                return

            p1, p2 = random.sample(persos, 2)
            nom1, nom2 = p1["nom"], p2["nom"]

            embed = discord.Embed(
                title="💥 Duel de popularité !",
                description=(
                    f"**{ctx.author.display_name}**, choisis entre :\n\n"
                    f"⚔️ **{nom1}**\n"
                    f"🛡️ **{nom2}**\n\n"
                    "Réagis avec ton préféré 👇"
                ),
                color=discord.Color.orange()
            )
            embed.set_footer(text="🕒 Tu as 30 secondes pour choisir.")

            message = await safe_send(ctx.channel, embed=embed)
            await message.add_reaction("⚔️")
            await message.add_reaction("🛡️")

            def check(reaction, user):
                return (
                    user == ctx.author
                    and str(reaction.emoji) in ["⚔️", "🛡️"]
                    and reaction.message.id == message.id
                )

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await safe_send(ctx.channel, "⏰ Temps écoulé. Vote annulé.")
                return

            selection = nom1 if str(reaction.emoji) == "⚔️" else nom2

            try:
                data = supabase.table("perso_votes").select("votes").eq("nom", selection).execute()
                if data.data:
                    votes = data.data[0]["votes"] + 1
                    supabase.table("perso_votes").update({"votes": votes}).eq("nom", selection).execute()
                else:
                    supabase.table("perso_votes").insert({"nom": selection, "votes": 1}).execute()

                await safe_send(ctx.channel, f"✅ {ctx.author.mention} a voté pour **{selection}** !")
            except Exception as db_error:
                await safe_send(ctx.channel, f"⚠️ Une erreur est survenue lors de l’enregistrement du vote : `{db_error}`")

        except FileNotFoundError:
            await safe_send(ctx.channel, "❌ Fichier `bleach_personnages.json` introuvable.")
        except Exception as e:
            await safe_send(ctx.channel, f"⚠️ Une erreur est survenue : `{e}`")

# ────────────────────────────────────────────────────────────────────────────────
# 🏆 TOP PERSOS - CLASSEMENT DES PERSONNAGES PRÉFÉRÉS
# ────────────────────────────────────────────────────────────────────────────────
class TopPersoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tupreftop",
        aliases=["toptupref", "tpt"],
        help="📊 Affiche les personnages les plus aimés pour la commande tupref."
    )
    async def topperso(self, ctx: commands.Context, limit: int = 10):
        if limit < 1 or limit > 50:
            await safe_send(ctx.channel, "❌ Le nombre doit être **entre 1 et 50** pour éviter de surcharger le classement.")
            return

        try:
            result = supabase.table("perso_votes") \
                             .select("nom", "votes") \
                             .order("votes", desc=True) \
                             .limit(limit) \
                             .execute()
        except Exception as e:
            await safe_send(ctx.channel, f"⚠️ Erreur lors de la récupération des données : `{e}`")
            return

        if not result.data:
            await safe_send(ctx.channel, "📉 Aucun vote n’a encore été enregistré. Sois le premier à voter !")
            return

        embed = discord.Embed(
            title=f"🏆 Top {limit} des personnages les plus aimés",
            color=discord.Color.gold()
        )

        medals = ["🥇", "🥈", "🥉"] + ["🔹"] * (limit - 3)
        classement = ""
        for i, row in enumerate(result.data, start=1):
            emoji = medals[i - 1] if i <= len(medals) else "🔹"
            classement += f"{emoji} {i}. {row['nom']} — 💖 {row['votes']} votes\n"

        embed.description = f"Classement des personnages les plus préférés avec la commande tupref.\n\n{classement}"
        embed.set_footer(text="🔥 Basé sur les votes enregistrés par la communauté")

        await safe_send(ctx.channel, embed=embed)

# ────────────────────────────────────────────────────────────────────────────────
# 🔄 COMMANDE ADMIN - RESET VOTES PERSOS (SUPABASE)
# ────────────────────────────────────────────────────────────────────────────────
class ResetPersoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tuprefreset",
        aliases=["tpr"],
        help="(Admin) Réinitialise tous les votes des personnages."
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def resetperso(self, ctx: commands.Context):
        try:
            result = supabase.table("perso_votes").delete().neq("nom", "").execute()
            if result.get("error"):
                raise Exception(result["error"]["message"])
            await safe_send(ctx.channel, "🗑️ Tous les votes ont été réinitialisés avec succès.")
        except Exception as e:
            await safe_send(ctx.channel, f"❌ Une erreur est survenue lors de la réinitialisation :\n```{e}```")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup des Cogs
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cogs = [TuPrefCommand(bot), TopPersoCommand(bot), ResetPersoCommand(bot)]
    for cog in cogs:
        for command in cog.get_commands():
            if not hasattr(command, "category"):
                command.category = "Bleach"
        await bot.add_cog(cog)
