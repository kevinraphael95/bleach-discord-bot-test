# ────────────────────────────────────────────────────────────────────────────────
# 📌 tasks/heartbeat.py — Tâche périodique de heartbeat pour garder le bot vivant
# Objectif : Envoyer régulièrement un ping à Supabase pour garder la trace
# Catégorie : Général
# Accès : Privé
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Modules standards
# ────────────────────────────────────────────────────────────────────────────────
import asyncio
from datetime import datetime, timezone

# ────────────────────────────────────────────────────────────────────────────────
# 🔁 Tâche heartbeat périodique
# ────────────────────────────────────────────────────────────────────────────────
async def heartbeat_task(bot):
    """
    Tâche qui tourne en boucle toutes les 60 secondes
    pour envoyer un ping dans Supabase.
    """
    while True:
        now = datetime.now(timezone.utc).isoformat()
        try:
            # Mise à jour dans Supabase (via bot.supabase)
            await bot.loop.run_in_executor(
                None,
                lambda: bot.supabase.table("bot_heartbeat").upsert({
                    "id": bot.INSTANCE_ID,
                    "last_ping": now
                }).execute()
            )
            print(f"[Heartbeat] Ping envoyé à {now}")
        except Exception as e:
            print(f"[Heartbeat] Erreur lors de l'envoi du ping : {e}")

        await asyncio.sleep(60)
