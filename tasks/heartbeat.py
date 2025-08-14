# ────────────────────────────────────────────────────────────────────────────────
# 📌 heartbeat.py — Task automatique d'envoi du heartbeat toutes les 5 minutes
# Objectif : Garder le bot alive en pingant régulièrement un salon configuré
# Catégorie : Général
# Accès : Interne (aucune commande ici)
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone
from utils.discord_utils import safe_send  # <-- Import safe_send

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class HeartbeatTask(commands.Cog):
    """
    Task qui envoie un message toutes les 5 minutes dans un salon configuré.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.supabase = bot.supabase
        self.heartbeat_channel_id = None
        self.heartbeat_task.start()

    def cog_unload(self):
        self.heartbeat_task.cancel()

    @tasks.loop(minutes=5)
    async def heartbeat_task(self):
        # 🔒 Vérifie si le heartbeat est en pause
        try:
            pause_res = self.supabase.table("bot_settings").select("value").eq("key", "heartbeat_paused").execute()
            if pause_res.data and pause_res.data[0]["value"].lower() == "true":
                print("[Heartbeat] Pausé — aucune action envoyée.")
                return
        except Exception as e:
            print(f"[Heartbeat] Erreur lecture du flag heartbeat_paused : {e}")

        if not self.heartbeat_channel_id:
            await self.load_heartbeat_channel()

        if self.heartbeat_channel_id:
            channel = self.bot.get_channel(self.heartbeat_channel_id)
            if channel:
                try:
                    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    await safe_send(channel, f"💓💓 Boom boom ! ({now})")  # <-- safe_send ici
                except Exception as e:
                    print(f"[Heartbeat] Erreur en envoyant le message : {e}")
            else:
                print("[Heartbeat] Salon non trouvé, pensez à reconfigurer le salon heartbeat.")

    @heartbeat_task.before_loop
    async def before_heartbeat(self):
        await self.bot.wait_until_ready()
        await self.load_heartbeat_channel()

    async def load_heartbeat_channel(self):
        try:
            resp = self.supabase.table("bot_settings").select("value").eq("key", "heartbeat_channel_id").execute()
            if resp.data and len(resp.data) > 0:
                val = resp.data[0]["value"]
                if val.isdigit():
                    self.heartbeat_channel_id = int(val)
                    print(f"[Heartbeat] Salon heartbeat chargé depuis Supabase : {self.heartbeat_channel_id}")
                else:
                    print("[Heartbeat] Valeur heartbeat_channel_id invalide en base.")
            else:
                print("[Heartbeat] Pas de salon heartbeat configuré en base.")
        except Exception as e:
            print(f"[Heartbeat] Erreur lecture Supabase : {e}")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(HeartbeatTask(bot))
