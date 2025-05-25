import discord
from discord.ext import commands
from supabase_client import supabase

class ResetPersosCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="resetpersos", help="(Admin) Réinitialise tous les votes des personnages.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def resetpersos(self, ctx):
        try:
            supabase.table("perso_votes").delete().neq("nom", "").execute()
            await ctx.send("🗑️ Tous les votes ont été réinitialisés avec succès.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : {e}")

# Chargement automatique
async def setup(bot):
    cog = ResetPersosCommand(bot)
    for command in cog.get_commands():
        command.category = "Fun"
    await bot.add_cog(cog)
