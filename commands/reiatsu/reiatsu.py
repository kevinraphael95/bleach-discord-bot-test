# ────────────────────────────────────────────────────────────────────────────────
# 📌 reiatsu.py — Commande interactive /reiatsu et !reiatsu
# Objectif : Affiche le profil complet Reiatsu et propose toutes les actions
# Catégorie : Reiatsu
# Accès : Public
# Cooldown : 1 utilisation / 3 secondes / utilisateur
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
from dateutil import parser
from datetime import datetime, timedelta
import time
import json
import random

from utils.supabase_client import supabase
from utils.discord_utils import safe_send, safe_respond

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Boutons interactifs Reiatsu
# ────────────────────────────────────────────────────────────────────────────────
class ReiatsuView(View):
    def __init__(self, author: discord.Member, spawn_link: str = None):
        super().__init__(timeout=None)
        self.author = author
        # Boutons disponibles
        if spawn_link:
            self.add_item(Button(label="💠 Aller au spawn", style=discord.ButtonStyle.link, url=spawn_link))
        self.add_item(Button(label="📊 Classement", style=discord.ButtonStyle.primary, custom_id="reiatsu:classement"))
        self.add_item(Button(label="⚡ Éveil", style=discord.ButtonStyle.success, custom_id="reiatsu:eveil"))
        self.add_item(Button(label="🎭 Changer de classe", style=discord.ButtonStyle.secondary, custom_id="reiatsu:classe"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser ce bouton.", ephemeral=True)
            return False
        return True

    # ── Classement
    @discord.ui.button(label="📊 Classement", style=discord.ButtonStyle.primary, custom_id="reiatsu:classement")
    async def classement_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        classement_data = supabase.table("reiatsu").select("user_id, points").order("points", desc=True).limit(10).execute()
        if not classement_data.data:
            return await interaction.response.send_message("Aucun classement disponible pour le moment.", ephemeral=True)

        description = ""
        for i, entry in enumerate(classement_data.data, start=1):
            user_id = int(entry["user_id"])
            points = entry["points"]
            user = interaction.guild.get_member(user_id) if interaction.guild else None
            name = user.display_name if user else f"Utilisateur ({user_id})"
            description += f"**{i}. {name}** — {points} points\n"

        embed = discord.Embed(title="📊 Classement Reiatsu", description=description, color=discord.Color.purple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── Éveil
    @discord.ui.button(label="⚡ Éveil", style=discord.ButtonStyle.success, custom_id="reiatsu:eveil")
    async def eveil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        user_data = supabase.table("reiatsu").select("points").eq("user_id", user_id).execute()
        if not user_data.data:
            return await interaction.response.send_message("❌ Pas de compte Reiatsu.", ephemeral=True)
        points = user_data.data[0]["points"]
        EVEIL_COST = 1
        if points < EVEIL_COST:
            return await interaction.response.send_message(f"⛔ Pas assez de points ({EVEIL_COST} requis).", ephemeral=True)

        # Menu choix de pouvoir
        view = View()
        for pouvoir in ["Shinigami", "Hollow", "Quincy", "Fullbring"]:
            view.add_item(Button(label=pouvoir, style=discord.ButtonStyle.primary, custom_id=f"eveil:{pouvoir}"))
        await interaction.response.send_message("Choisis ton pouvoir :", view=view, ephemeral=True)

    # ── Changer de classe
    @discord.ui.button(label="🎭 Changer de classe", style=discord.ButtonStyle.secondary, custom_id="reiatsu:classe")
    async def classe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        with open("data/classes.json", "r", encoding="utf-8") as f:
            CLASSES = json.load(f)
        options = [discord.SelectOption(label=f"{data.get('Symbole','🌀')} {classe}", description=data['Passive'][:100], value=classe) for classe, data in CLASSES.items()]
        select = Select(placeholder="Choisis ta classe", options=options, min_values=1, max_values=1)

        async def select_callback(i: discord.Interaction):
            classe = select.values[0]
            nouveau_cd = 19 if classe == "Voleur" else 24
            supabase.table("reiatsu").update({"classe": classe, "steal_cd": nouveau_cd}).eq("user_id", str(user_id)).execute()
            symbole = CLASSES[classe].get("Symbole","🌀")
            embed = discord.Embed(title=f"✅ Classe choisie : {symbole} {classe}", color=discord.Color.green())
            await i.response.edit_message(embed=embed, view=None)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Sélectionne ta classe :", view=view, ephemeral=True)


# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class ReiatsuCommand(commands.Cog):
    """Commande /reiatsu et !reiatsu — Affiche le profil Reiatsu complet et actions disponibles"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Profil complet
    async def _send_profile(self, ctx_or_interaction, author, guild, target_user):
        user = target_user or author
        user_id = str(user.id)
        guild_id = str(guild.id) if guild else None

        user_data = supabase.table("reiatsu").select("points, classe, last_steal_attempt, steal_cd").eq("user_id", user_id).execute()
        data = user_data.data[0] if user_data.data else {}
        points = data.get("points", 0)
        classe_nom = data.get("classe")
        last_steal_str = data.get("last_steal_attempt")
        steal_cd = data.get("steal_cd")

        with open("data/classes.json", "r", encoding="utf-8") as f:
            CLASSES = json.load(f)

        if classe_nom and classe_nom in CLASSES:
            classe_text = f"• Classe : **{classe_nom}**\n• Compétence passive : {CLASSES[classe_nom]['Passive']}\n• Compétence active : {CLASSES[classe_nom]['Active']}"
        else:
            classe_text = "Aucune classe sélectionnée."

        cooldown_text = "Disponible ✅"
        if classe_nom and steal_cd is None:
            steal_cd = 19 if classe_nom == "Voleur" else 24
            supabase.table("reiatsu").update({"steal_cd": steal_cd}).eq("user_id", user_id).execute()

        if last_steal_str and steal_cd:
            last_steal = parser.parse(last_steal_str)
            next_steal = last_steal + timedelta(hours=steal_cd)
            now = datetime.utcnow()
            if now < next_steal:
                restant = next_steal - now
                minutes_total = int(restant.total_seconds() // 60)
                h, m = divmod(minutes_total, 60)
                cooldown_text = f"{restant.days}j {h}h{m}m" if restant.days else f"{h}h{m}m"

        salon_text, temps_text, spawn_link = "❌", "❌", None
        if guild:
            config_data = supabase.table("reiatsu_config").select("*").eq("guild_id", guild_id).execute()
            config = config_data.data[0] if config_data.data else None
            salon_text = "❌ Aucun salon configuré"
            temps_text = "⚠️ Inconnu"
            if config:
                salon = guild.get_channel(int(config["channel_id"])) if config.get("channel_id") else None
                salon_text = salon.mention if salon else "⚠️ Salon introuvable"
                if config.get("en_attente"):
                    channel_id = config.get("channel_id")
                    msg_id = config.get("spawn_message_id")
                    if msg_id and channel_id:
                        spawn_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{msg_id}"
                        temps_text = f"Un Reiatsu 💠 est **déjà apparu** !"
                    else:
                        temps_text = "Un Reiatsu 💠 est déjà apparu (lien indisponible)"
                else:
                    last_spawn = config.get("last_spawn_at")
                    delay = config.get("delay_minutes", 1800)
                    if last_spawn:
                        remaining = int(parser.parse(last_spawn).timestamp() + delay - time.time())
                        if remaining <= 0:
                            temps_text = "💠 Un Reiatsu peut apparaître **à tout moment** !"
                        else:
                            minutes, seconds = divmod(remaining, 60)
                            temps_text = f"**{minutes}m {seconds}s**"
                    else:
                        temps_text = "💠 Un Reiatsu peut apparaître **à tout moment** !"

        embed = discord.Embed(
            title="__**💠 Profil**__",
            description=f"**{user.display_name}** a actuellement : **{points}** points de Reiatsu\n"
                        f"• 🕵️ Cooldown vol : {cooldown_text}\n"
                        f"\n__**Classe**__\n{classe_text}\n"
                        f"\n__**Spawn du reiatsu**__\n• 📍 Lieu : {salon_text}\n• ⏳ Temps avant apparition : {temps_text}",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Utilise les boutons ci-dessous pour interagir.")
        view = ReiatsuView(author, spawn_link=spawn_link)

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view)
        else:
            await safe_send(ctx_or_interaction, embed=embed, view=view)

    # ── Commande SLASH
    @app_commands.command(name="reiatsu", description="💠 Affiche le score de Reiatsu d’un membre")
    @app_commands.describe(member="Membre dont vous voulez voir le Reiatsu")
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: i.user.id)
    async def slash_reiatsu(self, interaction: discord.Interaction, member: discord.Member = None):
        try:
            await self._send_profile(interaction, interaction.user, interaction.guild, member)
        except app_commands.CommandOnCooldown as e:
            await safe_respond(interaction, f"⏳ Attends encore {e.retry_after:.1f}s.", ephemeral=True)
        except Exception as e:
            print(f"[ERREUR /reiatsu] {e}")
            await safe_respond(interaction, "❌ Une erreur est survenue.", ephemeral=True)

    # ── Commande PREFIX
    @commands.command(name="reiatsu", aliases=["rts"])
    @commands.cooldown(1, 3.0, commands.BucketType.user)
    async def prefix_reiatsu(self, ctx: commands.Context, member: discord.Member = None):
        try:
            await ctx.message.delete()
        except:
            pass
        await self._send_profile(ctx.channel, ctx.author, ctx.guild, member)

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = ReiatsuCommand(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Reiatsu"
    await bot.add_cog(cog)
