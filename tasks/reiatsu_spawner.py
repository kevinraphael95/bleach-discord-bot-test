# ──────────────────────────────────────────────────────────────
# 📁 REIATSU - GESTION DU SPAWN
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# 📦 IMPORTS
# ──────────────────────────────────────────────────────────────
import discord
import random
import time
from datetime import datetime
from dateutil import parser

from discord.ext import commands, tasks
from supabase_client import supabase

# ──────────────────────────────────────────────────────────────
# 🔧 COG : ReiatsuSpawner
# ──────────────────────────────────────────────────────────────
class ReiatsuSpawner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.spawn_loop.start()  # 🔁 Lancement automatique de la boucle

    def cog_unload(self):
        self.spawn_loop.cancel()  # 🛑 Arrêt de la boucle à l’unload

    # ──────────────────────────────────────────────────────────
    # ⏲️ TÂCHE : spawn_loop — toutes les 60 secondes
    # ──────────────────────────────────────────────────────────
    @tasks.loop(seconds=60)
    async def spawn_loop(self):
        await self.bot.wait_until_ready()

        # 🔒 Ne fait tourner la tâche que sur l'instance principale
        if not getattr(self.bot, "is_main_instance", True):
            return

        now = int(time.time())

        # 📦 Récupère la config des serveurs
        configs = supabase.table("reiatsu_config").select("*").execute()

        for conf in configs.data:
            guild_id = conf["guild_id"]
            channel_id = conf.get("channel_id")
            en_attente = conf.get("en_attente", False)
            delay = conf.get("delay_minutes") or 1800

            if not channel_id or en_attente:
                continue

            last_spawn_str = conf.get("last_spawn_at")
            should_spawn = not last_spawn_str or (
                now - int(parser.parse(last_spawn_str).timestamp()) >= delay
            )

            if not should_spawn:
                continue

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                continue

            # ✨ Envoie du message de spawn
            embed = discord.Embed(
                title="💠 Un Reiatsu sauvage apparaît !",
                description="Cliquez sur la réaction 💠 pour l'absorber.",
                color=discord.Color.purple()
            )
            message = await channel.send(embed=embed)
            await message.add_reaction("💠")

            # 💾 Mise à jour de l'état
            supabase.table("reiatsu_config").update({
                "en_attente": True,
                "last_spawn_at": datetime.utcnow().isoformat(),
                "spawn_message_id": str(message.id)
            }).eq("guild_id", guild_id).execute()

    # ──────────────────────────────────────────────────────────
    # 🎯 ÉVÉNEMENT : Réaction au spawn
    # ──────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "💠" or payload.user_id == self.bot.user.id:
            return

        guild_id = str(payload.guild_id)
        conf_data = supabase.table("reiatsu_config").select("*").eq("guild_id", guild_id).execute()
        if not conf_data.data:
            return

        conf = conf_data.data[0]
        if not conf.get("en_attente") or str(payload.message_id) != conf.get("spawn_message_id"):
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        user = guild.get_member(payload.user_id)
        if not channel or not user:
            return

        # 🎲 Détermine si c'est un Super Reiatsu (1% de chance)
        is_super = random.randint(1, 100) == 1
        gain = 100 if is_super else 1

        # ➕ Ajoute les points au joueur
        user_id = str(user.id)
        reiatsu = supabase.table("reiatsu").select("points").eq("user_id", user_id).execute()
        if reiatsu.data:
            points = reiatsu.data[0]["points"] + gain
            supabase.table("reiatsu").update({"points": points}).eq("user_id", user_id).execute()
        else:
            supabase.table("reiatsu").insert({
                "user_id": user_id,
                "username": user.name,
                "points": gain
            }).execute()

        # 📣 Message de confirmation
        if is_super:
            await channel.send(f"🌟 {user.mention} a absorbé un **Super Reiatsu** et gagné **+100** reiatsu !")
        else:
            await channel.send(f"💠 {user.mention} a absorbé le Reiatsu et gagné **+1** reiatsu !")

        # 🔄 Réinitialisation de l’état de spawn
        new_delay = random.randint(1800, 5400)
        supabase.table("reiatsu_config").update({
            "en_attente": False,
            "spawn_message_id": None,
            "delay_minutes": new_delay
        }).eq("guild_id", guild_id).execute()

# ──────────────────────────────────────────────────────────────
# 🔌 SETUP AUTOMATIQUE DU COG
# ──────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(ReiatsuSpawner(bot))
    print("✅ Cog chargé : ReiatsuSpawner (Spawn + Réactions)")
