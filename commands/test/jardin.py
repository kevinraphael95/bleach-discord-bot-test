# ────────────────────────────────────────────────────────────────────────────────
# 📌 jardin.py — Commande interactive /jardin et !jardin
# Objectif : Chaque utilisateur a un jardin persistant avec des fleurs
# Catégorie : Jeu
# Accès : Tout le monde
# ────────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────────────
# 📦 Imports nécessaires
# ────────────────────────────────────────────────────────────────────────────────
import os
import random
import datetime
import json
import discord
from discord import app_commands
from discord.ext import commands
from utils.supabase_client import supabase
from utils.discord_utils import safe_send, safe_respond

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 table name
# ────────────────────────────────────────────────────────────────────────────────
TABLE_NAME = "gardens"

# ────────────────────────────────────────────────────────────────────────────────
# 🌱 Chargement des constantes depuis un JSON
# ────────────────────────────────────────────────────────────────────────────────
with open("data/jardin_config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

DEFAULT_GRID = CONFIG["DEFAULT_GRID"]
DEFAULT_INVENTORY = CONFIG["DEFAULT_INVENTORY"]

FLEUR_EMOJIS = CONFIG["FLEUR_EMOJIS"]
FLEUR_VALUES = CONFIG["FLEUR_VALUES"]
FLEUR_SIGNS = CONFIG["FLEUR_SIGNS"]

FLEUR_LIST = list(FLEUR_EMOJIS.items())

FERTILIZE_COOLDOWN = datetime.timedelta(minutes=CONFIG["FERTILIZE_COOLDOWN_MINUTES"])
FERTILIZE_PROBABILITY = CONFIG["FERTILIZE_PROBABILITY"]

POTIONS = CONFIG["POTIONS"]


# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Fonctions utilitaires
# ────────────────────────────────────────────────────────────────────────────────
async def get_or_create_garden(user_id: int, username: str):
    res = supabase.table(TABLE_NAME).select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]

    new_garden = {
        "user_id": user_id,
        "username": username,
        "garden_grid": DEFAULT_GRID.copy(),
        "inventory": DEFAULT_INVENTORY.copy(),
        "argent": 0,
        "armee": "",
        "last_fertilize": None
    }
    supabase.table(TABLE_NAME).insert(new_garden).execute()
    return new_garden


def build_garden_embed(garden: dict, viewer_id: int) -> discord.Embed:
    lines = garden["garden_grid"]
    inv_dict = garden["inventory"]
    inv = " / ".join(f"{FLEUR_EMOJIS[f]}{inv_dict.get(f, 0)}" for f in FLEUR_EMOJIS)

    cd_str = "✅ Disponible"
    if garden.get("last_fertilize"):
        try:
            last_dt = datetime.datetime.fromisoformat(garden["last_fertilize"])
            now = datetime.datetime.now(datetime.timezone.utc)
            remain = last_dt + FERTILIZE_COOLDOWN - now
            if remain.total_seconds() > 0:
                total_seconds = int(remain.total_seconds())
                minutes, seconds = divmod(total_seconds, 60)
                hours, minutes = divmod(minutes, 60)
                cd_str = f"⏳ {hours}h {minutes}m {seconds}s"
        except Exception as e:
            print(f"[ERREUR parse last_fertilize] {e}")

    embed = discord.Embed(
        title=f"🏡 Jardin de {garden['username']}",
        description="\n".join(lines),
        color=discord.Color.green()
    )
    embed.add_field(
        name="Infos",
        value=f"Fleurs possédées : {inv}\n"
              f"Armée : {garden['armee'] or '—'} | Argent : {garden['argent']}💰\n"
              f"Cooldown engrais : {cd_str}",
        inline=False
    )
    return embed

def pousser_fleurs(lines: list[str]) -> list[str]:
    new_lines = []
    for line in lines:
        chars = []
        for c in line:
            if c == "🌱" and random.random() < FERTILIZE_PROBABILITY:
                _, emoji = random.choice(FLEUR_LIST)
                chars.append(emoji)
            else:
                chars.append(c)
        new_lines.append("".join(chars))
    return new_lines

def couper_fleurs(lines: list[str], garden: dict) -> tuple[list[str], dict]:
    new_lines = []
    inv = garden["inventory"]
    for line in lines:
        chars = []
        for c in line:
            for col, emoji in FLEUR_EMOJIS.items():
                if c == emoji:
                    inv[col] = inv.get(col, 0) + 1
                    c = "🌱"
            chars.append(c)
        new_lines.append("".join(chars))
    garden["inventory"] = inv
    return new_lines, garden

def build_potions_embed(potions: dict) -> discord.Embed:
    if not potions:
        desc = "🧪 Tu n’as aucune potion."
    else:
        # Tri par valeur croissante
        sorted_potions = dict(sorted(
            potions.items(),
            key=lambda x: next((int(v) for v, n in POTIONS.items() if n == x[0]), 0)
        ))
        desc = "\n".join(f"{name} x{qty}" for name, qty in sorted_potions.items())

    embed = discord.Embed(
        title="🧪 Tes potions",
        description=desc,
        color=discord.Color.teal()
    )
    return embed


# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Alchimie interactive
# ────────────────────────────────────────────────────────────────────────────────
class AlchimieView(discord.ui.View):
    def __init__(self, garden: dict, user_id: int, timeout=180):
        super().__init__(timeout=timeout)
        self.garden = garden
        self.user_id = user_id
        self.original_inventory = garden["inventory"].copy()  # inventaire réel sauvegardé
        self.temp_inventory = garden["inventory"].copy()      # inventaire temporaire
        self.value = 0
        self.selected_flowers = []

    def build_embed(self):
        fleurs_grouped = {"+" : [], "×" : [], "-" : []}
        for f in FLEUR_EMOJIS:
            sign = FLEUR_SIGNS[f]
            val = FLEUR_VALUES[f]
            fleurs_grouped[sign].append(f"{FLEUR_EMOJIS[f]}{sign}{val}")
        fleurs = "  ".join(" ".join(fleurs_grouped[s]) for s in ("+", "×", "-"))
        chosen = " ".join(FLEUR_EMOJIS[f] for f in self.selected_flowers) if self.selected_flowers else "—"

        return discord.Embed(
            title="⚗️ Alchimie",
            description=f"Valeurs de fleurs : {fleurs}\n\n⚗️ {chosen}\nValeur : **{self.value}**",
            color=discord.Color.purple()
        )

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    def use_flower(self, flower: str) -> bool:
        if self.temp_inventory.get(flower, 0) <= 0:
            return False
        self.temp_inventory[flower] -= 1
        self.selected_flowers.append(flower)

        sign = FLEUR_SIGNS[flower]
        val = FLEUR_VALUES[flower]
        if sign == "+":
            self.value += val
        elif sign == "-":
            self.value -= val
        elif sign == "×":
            self.value = self.value * val if self.value != 0 else val
        return True

    # ───────── Boutons fleurs ─────────
    @discord.ui.button(label="🌷", style=discord.ButtonStyle.green)
    async def add_tulipe(self, interaction, button):
        if not self.use_flower("tulipes"):
            return await interaction.response.send_message("❌ Tu n’as plus de 🌷 !", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="🌹", style=discord.ButtonStyle.green)
    async def add_rose(self, interaction, button):
        if not self.use_flower("roses"):
            return await interaction.response.send_message("❌ Tu n’as plus de 🌹 !", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="🪻", style=discord.ButtonStyle.green)
    async def add_jacinthe(self, interaction, button):
        if not self.use_flower("jacinthes"):
            return await interaction.response.send_message("❌ Tu n’as plus de 🪻 !", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="🌺", style=discord.ButtonStyle.green)
    async def add_hibiscus(self, interaction, button):
        if not self.use_flower("hibiscus"):
            return await interaction.response.send_message("❌ Tu n’as plus de 🌺 !", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="🌼", style=discord.ButtonStyle.green)
    async def add_paquerette(self, interaction, button):
        if not self.use_flower("paquerettes"):
            return await interaction.response.send_message("❌ Tu n’as plus de 🌼 !", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="🌻", style=discord.ButtonStyle.green)
    async def add_tournesol(self, interaction, button):
        if not self.use_flower("tournesols"):
            return await interaction.response.send_message("❌ Tu n’as plus de 🌻 !", ephemeral=True)
        await self.update_message(interaction)


    # ───────── Concocter & Reset ─────────
    @discord.ui.button(label="Concocter", emoji="⚗️", style=discord.ButtonStyle.blurple)
    async def concocter(self, interaction, button):
        potion = POTIONS.get(str(self.value))

        # 🔥 Mise à jour de l'inventaire réel
        garden_update = {"inventory": self.temp_inventory.copy()}

        if potion:
            # Récupérer les potions existantes
            user_data = supabase.table(TABLE_NAME).select("potions").eq("user_id", self.user_id).execute()
            potions_data = {}
            if user_data.data and user_data.data[0].get("potions"):
                potions_data = user_data.data[0]["potions"]

            # Ajouter la potion créée
            potions_data[potion] = potions_data.get(potion, 0) + 1

            # Trier les potions par valeur croissante
            sorted_potions = dict(sorted(
                potions_data.items(),
                key=lambda x: next((int(v) for v, n in POTIONS.items() if n == x[0]), 0)
            ))

            # Ajouter les potions triées à la mise à jour
            garden_update["potions"] = sorted_potions

            await interaction.response.send_message(f"✨ Tu as créé : **{potion}** !", ephemeral=False)
        else:
            await interaction.response.send_message("💥 Ta mixture explose ! Rien obtenu...", ephemeral=False)

        # 🔹 Mise à jour dans Supabase
        supabase.table(TABLE_NAME).update(garden_update).eq("user_id", self.user_id).execute()

        self.stop()



    @discord.ui.button(label="Reset", emoji="🔄", style=discord.ButtonStyle.red)
    async def reset(self, interaction, button):
        self.temp_inventory = self.original_inventory.copy()
        self.value = 0
        self.selected_flowers = []
        await self.update_message(interaction)

    async def interaction_check(self, interaction):
        return interaction.user.id == self.user_id

# ────────────────────────────────────────────────────────────────────────────────
# 🎛️ UI — Jardin avec grille cliquable + boutons
# ────────────────────────────────────────────────────────────────────────────────
class JardinView(discord.ui.View):
    def __init__(self, garden: dict, user_id: int):
        super().__init__(timeout=120)
        self.garden = garden
        self.user_id = user_id
        self.create_grid_buttons()
        self.add_control_buttons()

    def create_grid_buttons(self):
        # Supprime les boutons existants liés à la grille
        self.clear_items()
        for row_idx, row in enumerate(self.garden["garden_grid"]):
            for col_idx, emoji in enumerate(row):
                button = discord.ui.Button(
                    label=emoji,
                    style=discord.ButtonStyle.secondary,
                    row=row_idx,
                    custom_id=f"grid-{row_idx}-{col_idx}"
                )
                button.callback = self.make_cut_callback(row_idx, col_idx)
                self.add_item(button)

    def make_cut_callback(self, row_idx, col_idx):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message(
                    "❌ Ce jardin n'est pas à toi !", ephemeral=True
                )

            cell = self.garden["garden_grid"][row_idx][col_idx]
            for key, emoji in FLEUR_EMOJIS.items():
                if cell == emoji:
                    self.garden["inventory"][key] = self.garden["inventory"].get(key, 0) + 1
                    # Remplacer par 🌱
                    self.garden["garden_grid"][row_idx] = (
                        self.garden["garden_grid"][row_idx][:col_idx] + "🌱" +
                        self.garden["garden_grid"][row_idx][col_idx+1:]
                    )
                    # Mise à jour Supabase
                    await supabase.table(TABLE_NAME).update({
                        "garden_grid": self.garden["garden_grid"],
                        "inventory": self.garden["inventory"]
                    }).eq("user_id", self.user_id).execute()
                    # Recréer les boutons
                    self.create_grid_buttons()
                    self.add_control_buttons()
                    embed = build_garden_embed(self.garden, self.user_id)
                    await interaction.response.edit_message(embed=embed, view=self)
                    return
        return callback

    def add_control_buttons(self):
        # Engrais
        engrais_btn = discord.ui.Button(label="Engrais", emoji="💩", style=discord.ButtonStyle.green)
        engrais_btn.callback = self.engrais
        self.add_item(engrais_btn)

        # Alchimie
        alchimie_btn = discord.ui.Button(label="Alchimie", emoji="⚗️", style=discord.ButtonStyle.blurple)
        alchimie_btn.callback = self.alchimie
        self.add_item(alchimie_btn)

        # Potions
        potions_btn = discord.ui.Button(label="Potions", emoji="🧪", style=discord.ButtonStyle.green)
        potions_btn.callback = self.potions
        self.add_item(potions_btn)

    async def engrais(self, interaction: discord.Interaction):
        # Copier la logique existante de JardinView.engrais
        last = self.garden.get("last_fertilize")
        if last:
            try:
                last_dt = datetime.datetime.fromisoformat(last)
                now = datetime.datetime.now(datetime.timezone.utc)
                if now < last_dt + FERTILIZE_COOLDOWN:
                    remain = last_dt + FERTILIZE_COOLDOWN - now
                    total_seconds = int(remain.total_seconds())
                    minutes, seconds = divmod(total_seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    return await interaction.response.send_message(
                        f"⏳ Tu dois attendre {hours}h {minutes}m {seconds}s avant d'utiliser de l'engrais !",
                        ephemeral=True
                    )
            except Exception:
                pass
        self.garden["garden_grid"] = pousser_fleurs(self.garden["garden_grid"])
        self.garden["last_fertilize"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        await supabase.table(TABLE_NAME).update({
            "garden_grid": self.garden["garden_grid"],
            "last_fertilize": self.garden["last_fertilize"]
        }).eq("user_id", self.user_id).execute()
        self.create_grid_buttons()
        self.add_control_buttons()
        embed = build_garden_embed(self.garden, self.user_id)
        await interaction.response.edit_message(embed=embed, view=self)

    async def alchimie(self, interaction: discord.Interaction):
        view = AlchimieView(self.garden, self.user_id)
        embed = view.build_embed()
        await interaction.response.send_message(embed=embed, view=view)

    async def potions(self, interaction: discord.Interaction):
        user_data = supabase.table(TABLE_NAME).select("potions").eq("user_id", self.user_id).execute()
        potions_data = {}
        if user_data.data and user_data.data[0].get("potions"):
            potions_data = user_data.data[0]["potions"]
        embed = build_potions_embed(potions_data)
        await interaction.response.send_message(embed=embed, ephemeral=False)




# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class Jardin(commands.Cog):
    """Commande /jardin et !jardin — Voir son jardin"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _send_garden(self, target_user, viewer_id, respond_func):
        try:
            garden = await get_or_create_garden(target_user.id, target_user.name)
            embed = build_garden_embed(garden, viewer_id)
            view = None
            if target_user.id == viewer_id:
                view = JardinView(garden, viewer_id)
                view.update_buttons()
            await respond_func(embed=embed, view=view)
        except Exception as e:
            print(f"[ERREUR jardin] {e}")
            await respond_func("❌ Une erreur est survenue.", ephemeral=True)


    # ───────── Commande Slash ─────────
    @app_commands.command(name="jardin", description="Affiche ton jardin ou celui d'un autre utilisateur 🌱")
    @app_commands.checks.cooldown(1, 5.0)
    async def slash_jardin(self, interaction:discord.Interaction, user:discord.User=None):
        target = user or interaction.user
        await self._send_garden(target, interaction.user.id, lambda **kwargs: safe_respond(interaction, **kwargs))

    # ───────── Commande Préfixe ─────────
    @commands.command(name="jardin")
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def prefix_jardin(self, ctx:commands.Context, user:discord.User=None):
        target = user or ctx.author
        await self._send_garden(target, ctx.author.id, lambda **kwargs: safe_send(ctx.channel, **kwargs))

 

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = Jardin(bot)
    for command in cog.get_commands():
        if not hasattr(command, "category"):
            command.category = "Test"
    await bot.add_cog(cog)

