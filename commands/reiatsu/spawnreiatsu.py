import asyncio
import random
import time
from datetime import datetime
from dateutil import parser

import discord
from discord.ext import commands, tasks
from supabase_client import supabase

class ReiatsuSpawner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spawn_loop.add_exception_type(asyncio.CancelledError)
        self.spawn_loop.start()

    def cog_unload(self):
        self.spawn_loop.cancel()

    @tasks.loop(seconds=60)
    async def spawn_loop(self):
        await self.bot.wait_until_ready()

        if not getattr(self.bot, "is_main_instance", True):
            return  # Ne spawn que depuis une instance principale

        now = int(time.time())

        configs = supabase.table("reiatsu_config").select(
            "guild_id", "channel_id", "last_spawn_at", "delay_minutes", "en_attente"
        ).execute()

        for conf in configs.data:
            guild_id = conf["guild_id"]
            channel_id = conf.get("channel_id")
            en_attente = conf.get("en_attente", False)
            delay = conf.get("delay_minutes") or 1800

            if not channel_id or en_attente:
                continue

            last_spawn_str = conf.get("last_spawn_at")
            should_spawn = (
                not last_spawn_str or
                now - int(parser.parse(last_spawn_str).timestamp()) >= int(delay)
            )

            if not should_spawn:
                continue

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                continue

            # 🟣 Marque le spawn en attente
            embed = discord.Embed(
                title="💠 Un Reiatsu sauvage apparaît !",
                description="Cliquez sur la réaction 💠 pour l'absorber.",
                color=discord.Color.purple()
            )

            message = await channel.send(embed=embed)
            await message.add_reaction("💠")

            # 🔒 Mise à jour DB avec l’ID du message
            supabase.table("reiatsu_config").update({
                "en_attente": True,
                "last_spawn_at": datetime.utcnow().isoformat(),
                "spawn_message_id": str(message.id)
            }).eq("guild_id", guild_id).execute()

            def check(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction.emoji) == "💠" and
                    not user.bot
                )

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=10800.0, check=check)

                user_id = str(user.id)
                data = supabase.table("reiatsu").select("points").eq("user_id", user_id).execute()

                if data.data:
                    points = data.data[0]["points"] + 1
                    supabase.table("reiatsu").update({"points": points}).eq("user_id", user_id).execute()
                else:
                    supabase.table("reiatsu").insert({
                        "user_id": user_id,
                        "username": str(user.name),
                        "points": 1
                    }).execute()

                await channel.send(f"{user.mention} a absorbé le Reiatsu et gagné **+1** point !")

            except asyncio.TimeoutError:
                await channel.send("⏳ Le Reiatsu s'est dissipé dans l'air... personne ne l'a absorbé.")

            # ✅ Nouveau délai et déverrouillage
            new_delay = random.randint(1800, 5400)
            supabase.table("reiatsu_config").update({
                "delay_minutes": new_delay,
                "en_attente": False,
                "spawn_message_id": None
            }).eq("guild_id", guild_id).execute()


# 📦 Chargement
async def setup(bot):
    await bot.add_cog(ReiatsuSpawner(bot))
