# ────────────────────────────────────────────────────────────────────────────────
# 📌 fakenitro_proof.py — Commande interactive /fakenitro et !fakenitro
# Objectif : Générer un faux message Discord Nitro ultra réaliste (image HTML→PNG)
# Catégorie : Autre
# Accès : Tous
# Cooldown : 1 utilisation / 5 secondes / utilisateur
# ────────────────────────────────────────────────────────────────────────────────

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
import datetime, random, os, base64
from html2image import Html2Image

from utils.discord_utils import safe_send, safe_respond

# ────────────────────────────────────────────────────────────────────────────────
# 📂 Configuration
# ────────────────────────────────────────────────────────────────────────────────
hti = Html2Image(custom_flags=["--default-background-color=ffffff"])
hti.browser.use_new_headless = None

DEFAULT_AVATAR = "https://cdn.discordapp.com/embed/avatars/0.png"
current_directory = os.path.abspath(os.path.dirname(__file__))

def encode_font(font_path):
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode("utf-8")

font_b64 = encode_font(f"{current_directory}/assets/fonts/ggsans-regular.ttf")
fontmed_base64 = encode_font(f"{current_directory}/assets/fonts/ggsans-medium.ttf")

# ────────────────────────────────────────────────────────────────────────────────
# 🖼️ Génération HTML → Image
# ────────────────────────────────────────────────────────────────────────────────
class BoostPage:
    def __init__(self, nitro_type, authorname, authoravatar, authortext, receiveravatar, receivername, receivertext):
        self.actual_datetime = datetime.datetime.now()
        self.nitro_type = nitro_type
        self.authorname = authorname
        self.authoravatar = authoravatar
        self.authortext = authortext
        self.sender_message_datetime = (self.actual_datetime - datetime.timedelta(minutes=random.randint(1, 300))).strftime('Today at %I:%M %p')
        self.receivername = receivername
        self.receiveravatar = receiveravatar
        self.receivertext = receivertext
        self.receiver_message_datetime = (self.actual_datetime + datetime.timedelta(minutes=random.randint(1, 120))).strftime('Today at %I:%M %p')
        self.proof = ""

    def get_proof(self):
        nitro_links = {
            "classic": ("https://discord.gift/", f"file://{current_directory}/assets/nitro_presets/nitro_classic_preset.png"),
            "promo": ("https://discord.com/billing/promotions/", f"file://{current_directory}/assets/nitro_presets/nitro_promo_preset.png"),
            "boost": ("https://discord.gift/", f"file://{current_directory}/assets/nitro_presets/nitro_boost_preset.png")
        }
        nitro_link, nitro_image = nitro_links.get(self.nitro_type.lower(), nitro_links["boost"])
        with open(f"{current_directory}/assets/index.html", 'r') as boost_page:
            self.proof = boost_page.read() \
                .replace('GGSANSFONT', f"data:font/ttf;base64,{font_b64}") \
                .replace('GGSANSMEDIUMFONT', f"data:font/ttf;base64,{fontmed_base64}") \
                .replace('AUTHORNAME', self.authorname) \
                .replace('AUTHORAVATAR', self.authoravatar) \
                .replace('AUTHORDATETIME', self.sender_message_datetime) \
                .replace('AUTHORTEXT', self.authortext) \
                .replace('USERNAME', self.receivername) \
                .replace('USERAVATAR', self.receiveravatar) \
                .replace('USERDATETIME', self.receiver_message_datetime) \
                .replace('USERTEXT', self.receivertext) \
                .replace('NITROLINK', nitro_link) \
                .replace('NITROCODE', ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(16))) \
                .replace('NITROIMAGESRC', nitro_image)
        return self.proof

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Cog principal
# ────────────────────────────────────────────────────────────────────────────────
class FakeNitroProof(commands.Cog):
    """Commande /fakenitro et !fakenitro — Génère un faux message Nitro ultra réaliste"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("✅ Cog FakeNitroProof chargé")  # debug pour vérifier le chargement

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 Modal unique (fusion custom + id)
    # ────────────────────────────────────────────────────────────────────────────
    class NitroProofModal(Modal, title='Fake Nitro Proof System'):
        nitrotype = TextInput(label='Type of Nitro code', style=discord.TextStyle.short, placeholder='classic/boost/promo', required=True)
        authortext = TextInput(label='Text sent by you', style=discord.TextStyle.long, required=False)
        receiver_input = TextInput(label='Receiver (ID or Name)', style=discord.TextStyle.short, required=True)
        receiveravatar = TextInput(label='Receiver Avatar URL (optional)', style=discord.TextStyle.short, required=False)
        receivertext = TextInput(label='Text sent by receiver', style=discord.TextStyle.paragraph, required=True)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                # Si c'est un ID, fetch user
                try:
                    receiver = await interaction.client.fetch_user(int(self.receiver_input.value))
                    receiver_name = receiver.name
                    receiver_avatar = receiver.display_avatar.url if receiver.avatar else DEFAULT_AVATAR
                except:
                    receiver_name = self.receiver_input.value
                    receiver_avatar = self.receiveravatar.value or DEFAULT_AVATAR

                author_avatar = interaction.user.display_avatar.url if interaction.user.avatar else DEFAULT_AVATAR
                proof_html = BoostPage(
                    self.nitrotype.value,
                    interaction.user.display_name,
                    author_avatar,
                    self.authortext.value,
                    receiver_avatar,
                    receiver_name,
                    self.receivertext.value
                ).get_proof()

                hti.screenshot(html_str=proof_html, size=(random.randint(730, 1100), random.randint(450, 470)), save_as='proof.png')
                await interaction.user.send(file=discord.File('proof.png'))
                await interaction.followup.send("✅ Proof generated! Check your DMs.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 Commande préfixe !fakenitro
    # ────────────────────────────────────────────────────────────────────────────
    @commands.command(name="fakenitro", help="Generate a Giveaway Nitro Proof")
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    async def prefixed_proof(self, ctx):
        await ctx.send_modal(self.NitroProofModal())

    # ────────────────────────────────────────────────────────────────────────────
    # 🔹 Slash command /fakenitro
    # ────────────────────────────────────────────────────────────────────────────
    @app_commands.command(
        name="fakenitro",
        description="Generate a Giveaway Nitro Proof"
    )
    async def slash_proof(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.NitroProofModal())

# ────────────────────────────────────────────────────────────────────────────────
# 🔌 Setup du Cog
# ────────────────────────────────────────────────────────────────────────────────
async def setup(bot: commands.Bot):
    cog = FakeNitroProof(bot)
    await bot.add_cog(cog)
    try:
        bot.tree.add_command(cog.slash_proof)
        await bot.tree.sync()
        print("✅ Slash command /fakenitro enregistrée et synchronisée")
    except Exception as e:
        print(f"❌ Impossible d'ajouter la slash command: {e}")
