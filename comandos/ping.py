import nextcord
from nextcord.ext import commands

class Ping(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help="Muestra la latencia del bot")
  async def ping(self, ctx):
    await ctx.send(f'Mi latencia es {round(self.bot.latency * 1000, 2)}ms')

async def setup(bot):
  bot.add_cog(Ping(bot))