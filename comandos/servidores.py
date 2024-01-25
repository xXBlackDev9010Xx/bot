import nextcord
from nextcord.ext import commands

class Servidores(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def servidores(self, ctx):
    for guild in self.bot.guilds:
      await ctx.send(f"{guild.name} - {guild.id}")
    

async def setup(bot):
  bot.add_cog(Servidores(bot))