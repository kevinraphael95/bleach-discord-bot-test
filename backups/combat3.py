# ────────────────────────────────────────────────────────────────────────────────
# 📌 combat.py — Commande interactive !combat
# Objectif : Simule un combat entre 2 personnages de Bleach avec stats, énergie et effets.
# Catégorie : Bleach
# Accès : Public
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands
import random
import json
import os

# Import des fonctions utilitaires safe_send
from discord_utils import safe_send

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Chargement des personnages
# ────────────────────────────────────────────────────────────────────────────────
DATA_JSON_PATH = os.path.join("data", "bleach_personnages.json")

def load_personnages():
    """Charge les personnages depuis le fichier JSON."""
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# (Les fonctions init_personnage, formater_etat, appliquer_soin, appliquer_bouclier, infliger_degats, appliquer_effet restent inchangées)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Combat3Command(commands.Cog):
    """
    Commande !combat — Simule un combat entre 2 personnages de Bleach avec stats, énergie et effets.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="combat3",
        help="Simule un combat entre 2 personnages de Bleach.",
        description="Lance un combat automatisé sur 5 tours entre 2 personnages tirés au hasard."
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def combat(self, ctx: commands.Context):
        """Commande principale simulant un combat."""
        try:
            personnages = load_personnages()

            if len(personnages) < 2:
                return await safe_send(ctx.channel, "❌ Pas assez de personnages dans le fichier.")

            p1, p2 = random.sample(personnages, 2)
            for p in (p1, p2): init_personnage(p)

            nom1 = p1["nom"]
            nom2 = p2["nom"]

            # Détermine l'ordre des tours en fonction de la mobilité
            tour_order = sorted([p1, p2], key=lambda p: p["stats"]["mobilité"] + random.randint(0, 10), reverse=True)
            log = ""

            for tour in range(1, 6):
                log += f"**🌀 __Tour {tour}__ 🌀**\n{formater_etat(p1)}\n{formater_etat(p2)}\n\n"
                for attaquant in tour_order:
                    defenseur = p2 if attaquant == p1 else p1

                    if attaquant["vie"] <= 0 or defenseur["vie"] <= 0:
                        continue

                    # Gestion des status
                    if attaquant["status"] == "gel":
                        log += f"❄️ **{attaquant['nom']}** est gelé et ne peut pas agir.\n\n"
                        attaquant["status_duree"] -= 1
                        if attaquant["status_duree"] <= 0:
                            attaquant["status"] = None
                        continue

                    if attaquant["status"] == "confusion" and random.random() < 0.4:
                        log += f"💫 **{attaquant['nom']}** est confus et se blesse (10 PV) !\n\n"
                        attaquant["vie"] -= 10
                        attaquant["status_duree"] -= 1
                        if attaquant["status_duree"] <= 0:
                            attaquant["status"] = None
                        continue

                    if attaquant["status"] == "poison":
                        log += f"☠️ **{attaquant['nom']}** perd 5 PV à cause du poison.\n"
                        attaquant["vie"] -= 5
                        attaquant["status_duree"] -= 1
                        if attaquant["status_duree"] <= 0:
                            attaquant["status"] = None

                    # Choix des attaques utilisables
                    possibles = [
                        a for a in attaquant["attaques"]
                        if a["cout"] <= attaquant["energie"] and (a["type"] != "ultime" or not a["utilisé"])
                    ]

                    # Si aucune attaque normale n'est possible, utiliser attaque simple quelle que soit l'énergie
                    if not possibles:
                        cout_attaque_simple = 0 if attaquant["energie"] > defenseur["energie"] else min(10, attaquant["energie"])
                        degats = attaquant["stats"]["force"] // 2
                        attaque = {
                            "nom": "Attaque simple",
                            "degats": degats,
                            "cout": cout_attaque_simple,
                            "effet": ""
                        }

                    else:
                        attaque = random.choice(possibles)
                        if attaque["type"] == "ultime":
                            attaque["utilisé"] = True

                    esquive_chance = min(defenseur["stats"]["mobilité"] / 40 + random.uniform(0, 0.2), 0.5)
                    tentative = random.random()
                    cout_esquive = 50 if attaque["type"] == "ultime" else 10

                    # Tentative d'esquive
                    if tentative < esquive_chance and defenseur["energie"] >= cout_esquive:
                        defenseur["energie"] -= cout_esquive
                        log += f"💨 **{defenseur['nom']}** esquive **{attaque['nom']}** !\n"
                        if random.random() < 0.2:
                            contre = 10 + defenseur["stats"]["attaque"] // 2
                            attaquant["vie"] -= contre
                            log += f"🔁 Contre-attaque ! {attaquant['nom']} subit {contre} dégâts !\n"
                            if attaquant["vie"] <= 0:
                                log += f"\n🏆 **{defenseur['nom']} gagne par contre-attaque !**"
                                return await self.send_embed_log(ctx, log, nom1, nom2)
                        log += "\n"
                        continue

                    elif tentative < esquive_chance:
                        log += f"⚡ {defenseur['nom']} voulait esquiver mais manque d'énergie !\n"

                    # Calcul dégâts
                    base = attaque["degats"]
                    bonus = (
                        attaquant["stats"]["attaque"] +
                        attaquant["stats"]["force"] -
                        defenseur["stats"]["défense"] +
                        attaquant["stats"]["pression"] // 5
                    )
                    total = base + max(0, bonus)

                    # Critique
                    if random.random() < min(0.1 + attaquant["stats"]["force"] / 50, 0.4):
                        total = int(total * 1.5)
                        log += "**Coup critique ! **"

                    # Dépense énergie attaque
                    attaquant["energie"] -= attaque["cout"]

                    # Application des dégâts (avec bouclier)
                    log += f"💥 **{attaquant['nom']}** utilise **{attaque['nom']}**\n"
                    log = infliger_degats(defenseur, total, log)

                    # Application des effets spéciaux
                    # Note : pour soin ou bouclier, on applique à l'attaquant
                    if attaque.get("effet", "").lower() in ["soin", "bouclier"]:
                        log = appliquer_effet(attaque, attaquant, log)
                    else:
                        log = appliquer_effet(attaque, defenseur, log)

                    # Vérification KO
                    if defenseur["vie"] <= 0:
                        log += f"\n🏆 **{attaquant['nom']} remporte le combat par KO !**"
                        return await self.send_embed_log(ctx, log, nom1, nom2)

                    log += "\n"

            gagnant = p1 if p1["vie"] > p2["vie"] else p2
            log += f"🏁 Fin du combat, vainqueur : **{gagnant['nom']}** !"
            await self.send_embed_log(ctx, log, nom1, nom2)

        except Exception as e:
            print(f"[ERREUR !combat] {e}")
            await safe_send(ctx.channel, "❌ Une erreur est survenue lors de la simulation du combat.")

    async def send_embed_log(self, ctx, log: str, nom1: str, nom2: str):
        """Envoie le log dans un embed, tronque si trop long."""
        MAX_EMBED_DESC = 6000
        if len(log) > MAX_EMBED_DESC:
            log = log[:MAX_EMBED_DESC - 50] + "\n...[log tronqué]..."

        embed = discord.Embed(
            title=f"🗡️ {nom1} vs {nom2}",
            description=log,
            color=discord.Color.red()
        )
        await safe_send(ctx.channel, embed=embed)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Combat3Command(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Bleach"
    await bot.add_cog(cog)
