# ────────────────────────────────────────────────────────────────────────────────
# 📌 competence_active.py — Commande interactive !!ca
# Objectif : Activer la compétence active selon la classe du joueur avec cooldown
# Catégorie : VAACT
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
from datetime import datetime, timedelta

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Fonctions utilitaires pour la base de données (à remplacer par tes requêtes réelles)
# ────────────────────────────────────────────────────────────────────────────────

async def db_get_player_class_and_cd(bot, user_id):
    # Récupère classe et cooldown 'comp' pour user_id depuis Supabase
    response = await bot.supabase.from_("reiatsu").select("classe, comp").eq("user_id", str(user_id)).single()
    if response.get("error") or response.get("data") is None:
        return None, None
    data = response["data"]
    classe = data.get("classe")
    comp_cd_str = data.get("comp")
    if comp_cd_str:
        comp_cd = datetime.fromisoformat(comp_cd_str)
    else:
        comp_cd = None
    return classe, comp_cd

async def db_update_comp_cd(bot, user_id, new_cd):
    iso_cd = new_cd.isoformat()
    await bot.supabase.from_("reiatsu").update({"comp": iso_cd}).eq("user_id", str(user_id))

async def db_set_flag(bot, user_id, flag_name, value=True):
    await bot.supabase.from_("reiatsu").update({flag_name: value}).eq("user_id", str(user_id))

async def db_place_fake_reiatsu(bot, user_id):
    # Exemple d'insertion d'un piège reiatsu dans une autre table
    await bot.supabase.from_("pieges_reiatsu").insert({"user_id": str(user_id), "created_at": datetime.utcnow().isoformat()})

def lancer_pari():
    import random
    if random.random() < 0.5:
        return -10
    else:
        return random.randint(5, 50)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class CompetenceActive(commands.Cog):
    """
    Commande !!ca — Active la compétence active de la classe du joueur (cooldown global)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="ca",
        help="Active la compétence active de ta classe (cooldown 8h à 12h selon la compétence).",
        description="Commande pour activer ta compétence active selon ta classe."
    )
    async def ca(self, ctx: commands.Context):
        user_id = ctx.author.id
        try:
            classe, comp_cd = await db_get_player_class_and_cd(self.bot, user_id)
            if classe is None:
                await ctx.send("❌ Impossible de trouver ta classe dans la base de données.")
                return

            now = datetime.utcnow()
            if comp_cd and now < comp_cd:
                remaining = comp_cd - now
                heures = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                await ctx.send(f"⏳ Ta compétence active est en cooldown, disponible dans {heures}h {minutes}min.")
                return

            cooldowns = {
                "Voleur": 12,
                "Absorbeur": 12,
                "Illusionniste": 8,
                "Parieur": 12
            }

            if classe == "Voleur":
                await db_set_flag(self.bot, user_id, "vol_garanti", True)
                message = "🗡️ Vol garanti activé, valable pour ton prochain vol."

            elif classe == "Absorbeur":
                await db_set_flag(self.bot, user_id, "super_absorption", True)
                message = "💥 Super absorption activée pour ta prochaine absorption."

            elif classe == "Illusionniste":
                await db_place_fake_reiatsu(self.bot, user_id)
                message = "🎭 Piège reiatsu placé, attention aux prochains joueurs."

            elif classe == "Parieur":
                gain = lancer_pari()
                if gain > 0:
                    message = f"🎲 Pari réussi ! Tu as gagné {gain} reiatsu."
                else:
                    message = f"🎲 Pari perdu ! Tu as perdu 10 reiatsu."

            else:
                await ctx.send("❌ Tu n'as pas de classe valide ou pas de compétence active.")
                return

            new_cd = now + timedelta(hours=cooldowns.get(classe, 12))
            await db_update_comp_cd(self.bot, user_id, new_cd)

            await ctx.send(message)

        except Exception as e:
            print(f"[ERREUR !!ca] {e}")
            await ctx.send("❌ Une erreur est survenue lors de l'activation de ta compétence.")

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = CompetenceActive(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Reiatsu"
    await bot.add_cog(cog)
