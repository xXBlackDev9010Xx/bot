import nextcord
from nextcord.ext import commands

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help="Muestra esta lista de comandos")
  async def help(self, ctx):
    embed = nextcord.Embed(title="Comandos", description="Aqui están todos los comandos disponibles:", color=0x00ff00)

    for command in self.bot.commands:
      embed.add_field(name=f"r/{command.name}", value=command.help, inline=False)

    await ctx.send(embed=embed)

async def setup(bot):
  bot.add_cog(Help(bot))