# ────────────────────────────────────────────────────────────────────────────────
# 📌 heartbeat_admin.py — Commandes pour activer ou désactiver le heartbeat
# Objectif : Donner aux admins un moyen de contrôler le heartbeat dynamiquement
# Catégorie : Heartbeat
# Accès : Modérateur (permission admin requise)
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands

class HeartbeatAdmin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.supabase = bot.supabase

    @commands.command(name="pauseheartbeat", help="Pause le heartbeat automatique.", description="Désactive temporairement le heartbeat.")
    @commands.has_permissions(administrator=True)
    async def pauseheartbeat(self, ctx: commands.Context):
        try:
            self.supabase.table("bot_settings").upsert({
                "key": "heartbeat_paused",
                "value": "true"
            }).execute()
            await ctx.send("⏸️ Heartbeat mis en pause.")
        except Exception as e:
            print(f"[pauseheartbeat] Erreur : {e}")
            await ctx.send("❌ Erreur en mettant en pause le heartbeat.")

    @commands.command(name="resumeheartbeat", help="Relance le heartbeat automatique.", description="Réactive le heartbeat.")
    @commands.has_permissions(administrator=True)
    async def resumeheartbeat(self, ctx: commands.Context):
        try:
            self.supabase.table("bot_settings").upsert({
                "key": "heartbeat_paused",
                "value": "false"
            }).execute()
            await ctx.send("▶️ Heartbeat relancé.")
        except Exception as e:
            print(f"[resumeheartbeat] Erreur : {e}")
            await ctx.send("❌ Erreur en relançant le heartbeat.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = HeartbeatAdmin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Heartbeat"
    await bot.add_cog(cog)
    print("✅ Cog chargé : HeartbeatAdmin (catégorie = Heartbeat)")
