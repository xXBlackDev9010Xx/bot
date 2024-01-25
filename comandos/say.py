import nextcord
from nextcord.ext import commands

class Say(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help="Repite un mensaje")
  async def say(self, ctx, *, msg=None):
    if msg == None:
      return await ctx.send('Debes de colocar un mensaje')
    await ctx.send(msg)
    await ctx.message.delete()


async def setup(bot):
  bot.add_cog(Say(bot))