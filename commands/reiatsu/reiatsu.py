# ──────────────────────────────────────────────────────────────
# 📁 REIATSU - AFFICHAGE DE SCORE + INTERACTIONS
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from supabase_client import supabase
from datetime import datetime
import time
from dateutil import parser

# ──────────────────────────────────────────────────────────────
# COG PRINCIPAL
# ──────────────────────────────────────────────────────────────
class ReiatsuCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────────
    # COMMANDE PRINCIPALE
    # ──────────────────────────────────────────────────────────────
    @commands.command(
        name="reiatsu",
        aliases=["rts"],
        help="💠 Affiche le score de Reiatsu d’un membre (ou soi-même)."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def reiatsu(self, ctx: commands.Context, member: discord.Member = None):
        user = member or ctx.author
        user_id = str(user.id)
        guild_id = str(ctx.guild.id)

        # Récupération des points
        data = supabase.table("reiatsu") \
                       .select("points") \
                       .eq("user_id", user_id) \
                       .execute()
        points = data.data[0]["points"] if data.data else 0

        # Création de l'embed principal
        embed = discord.Embed(
            title="💠 Score de Reiatsu",
            description=f"{user.mention} a **{points}** points de Reiatsu.",
            color=user.color if user.color.value != 0 else discord.Color.blue()
        )
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.timestamp = ctx.message.created_at

        # Ajout des infos secondaires
        salon_info = await self.get_reiatsu_channel_info(ctx)
        timer_info = await self.get_reiatsu_timer_info(ctx)
        if salon_info:
            embed.add_field(name="📍 Salon Reiatsu", value=salon_info, inline=False)
        if timer_info:
            embed.add_field(name="⏳ Prochain spawn", value=timer_info, inline=False)

        # Envoi de l'embed
        msg = await ctx.send(embed=embed)

        # Réaction pour afficher le classement
        emoji = "📊"
        await msg.add_reaction(emoji)

        # Attente d'une réaction
        def check(reaction, user_react):
            return (
                reaction.message.id == msg.id
                and user_react.id == ctx.author.id
                and str(reaction.emoji) == emoji
            )

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            await msg.remove_reaction(reaction.emoji, ctx.author)
            await self.send_reiatsu_top(ctx)
        except Exception:
            pass  # Timeout ignoré

    # ──────────────────────────────────────────────────────────────
    # MÉTHODES SECONDAIRES (INFOS EN TEXTE POUR L'EMBED)
    # ──────────────────────────────────────────────────────────────

    async def get_reiatsu_channel_info(self, ctx):
        guild_id = str(ctx.guild.id)
        data = supabase.table("reiatsu_config").select("channel_id").eq("guild_id", guild_id).execute()
        if data.data:
            channel_id = int(data.data[0]["channel_id"])
            channel = self.bot.get_channel(channel_id)
            if channel:
                return f"{channel.mention}"
            else:
                return "⚠️ Le salon configuré n'existe plus."
        return "❌ Aucun salon configuré avec `!setreiatsu`."

    async def get_reiatsu_timer_info(self, ctx):
        guild_id = str(ctx.guild.id)
        res = supabase.table("reiatsu_config").select("*").eq("guild_id", guild_id).execute()
        if not res.data:
# ──────────────────────────────────────────────────────────────
# 📁 REIATSU - AFFICHAGE DE SCORE + INTERACTIONS
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from supabase_client import supabase
from datetime import datetime
import time
from dateutil import parser

# ──────────────────────────────────────────────────────────────
# COG PRINCIPAL
# ──────────────────────────────────────────────────────────────
class ReiatsuCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────────
    # COMMANDE PRINCIPALE
    # ──────────────────────────────────────────────────────────────
    @commands.command(
        name="reiatsu",
        aliases=["rts"],
        help="💠 Affiche le score de Reiatsu d’un membre (ou soi-même)."
    )
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def reiatsu(self, ctx: commands.Context, member: discord.Member = None):
        user = member or ctx.author
        user_id = str(user.id)
        guild_id = str(ctx.guild.id)

        # Récupération des points
        data = supabase.table("reiatsu") \
                       .select("points") \
                       .eq("user_id", user_id) \
                       .execute()
        points = data.data[0]["points"] if data.data else 0

        # Création de l'embed principal
        embed = discord.Embed(
            title="💠 Score de Reiatsu",
            description=f"{user.mention} a **{points}** points de Reiatsu.",
            color=user.color if user.color.value != 0 else discord.Color.blue()
        )
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.timestamp = ctx.message.created_at

        # Ajout des infos secondaires
        salon_info = await self.get_reiatsu_channel_info(ctx)
        timer_info = await self.get_reiatsu_timer_info(ctx)
        if salon_info:
            embed.add_field(name="📍 Salon Reiatsu", value=salon_info, inline=False)
        if timer_info:
            embed.add_field(name="⏳ Prochain spawn", value=timer_info, inline=False)

        # Envoi de l'embed
        msg = await ctx.send(embed=embed)

        # Réaction pour afficher le classement
        emoji = "📊"
        await msg.add_reaction(emoji)

        # Attente d'une réaction
        def check(reaction, user_react):
            return (
                reaction.message.id == msg.id
                and user_react.id == ctx.author.id
                and str(reaction.emoji) == emoji
            )

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            await msg.remove_reaction(reaction.emoji, ctx.author)
            await self.send_reiatsu_top(ctx)
        except Exception:
            pass  # Timeout ignoré

    # ──────────────────────────────────────────────────────────────
    # MÉTHODES SECONDAIRES (INFOS EN TEXTE POUR L'EMBED)
    # ──────────────────────────────────────────────────────────────

    async def get_reiatsu_channel_info(self, ctx):
        guild_id = str(ctx.guild.id)
        data = supabase.table("reiatsu_config").select("channel_id").eq("guild_id", guild_id).execute()
        if data.data:
            channel_id = int(data.data[0]["channel_id"])
            channel = self.bot.get_channel(channel_id)
            if channel:
                return f"{channel.mention}"
            else:
                return "⚠️ Le salon configuré n'existe plus."
        return "❌ Aucun salon configuré avec `!setreiatsu`."

    async def get_reiatsu_timer_info(self, ctx):
        guild_id = str(ctx.guild.id)
        res = supabase.table("reiatsu_config").select("*").eq("guild_id", guild_id).execute()
        if not res.data:
            return None
        conf = res.data[0]

        if conf.get("en_attente"):
            chan_id = conf.get("channel_id")
            msg_id = conf.get("spawn_message_id")
            if chan_id and msg_id:
                channel = ctx.guild.get_channel(int(chan_id))
                if channel:
                    try:
                        await channel.fetch_message(int(msg_id))
                        return "💠 Un Reiatsu est **déjà apparu** !"
                    except discord.NotFound:
                        return "💠 Un Reiatsu est **déjà apparu**, mais son message est introuvable."
            return "💠 Un Reiatsu est **déjà apparu**."
        
        delay = conf.get("delay_minutes", 1800)
        last_spawn_str = conf.get("last_spawn_at")
        if not last_spawn_str:
            return "**à tout moment** !"

        last_spawn_ts = parser.parse(last_spawn_str).timestamp()
        now = time.time()
        remaining = int((last_spawn_ts + delay) - now)

        if remaining <= 0:
            return "**à tout moment** !"
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            return f"**{minutes}m {seconds}s**"

    # 🏆 Affiche le classement des 10 meilleurs joueurs
    async def send_reiatsu_top(self, ctx):
        result = supabase.table("reiatsu").select("username", "points").order("points", desc=True).limit(10).execute()
        if not result.data:
            await ctx.send("📉 Aucun Reiatsu n’a encore été collecté.")
            return

        embed = discord.Embed(
            title="🏆 Classement Reiatsu - Top 10",
            description="Voici les utilisateurs avec le plus de **points de Reiatsu**.",
            color=discord.Color.purple()
        )
        for i, row in enumerate(result.data, start=1):
            embed.add_field(name=f"**{i}.** {row['username']}", value=f"💠 {row['points']} points", inline=False)
        await ctx.send(embed=embed)

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(ReiatsuCommand(bot))
    print("✅ Cog chargé : ReiatsuCommand (catégorie = Reiatsu)")

le("reiatsu").select("username", "points").order("points", desc=True).limit(10).execute()
        if not result.data:
            await ctx.send("📉 Aucun Reiatsu n’a encore été collecté.")
            return

        embed = discord.Embed(
            title="🏆 Classement Reiatsu - Top 10",
            description="Voici les utilisateurs avec le plus de **points de Reiatsu**.",
            color=discord.Color.purple()
        )
        for i, row in enumerate(result.data, start=1):
            embed.add_field(name=f"**{i}.** {row['username']}", value=f"💠 {row['points']} points", inline=False)
        await ctx.send(embed=embed)

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP POUR CHARGEMENT AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(ReiatsuCommand(bot))
    print("✅ Cog chargé : ReiatsuCommand (catégorie = Reiatsu)")
