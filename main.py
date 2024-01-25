import nextcord
import os
import asyncio
import difflib
from nextcord.ext import commands
from keep_alive import keep_alive

bot = commands.Bot(command_prefix="r/", intents=nextcord.Intents.all())
bot.remove_command("help")

async def load():
  for filename in os.listdir('./comandos'):
    if filename.endswith('.py'):
      cog_name = filename[:-3]
      try:
        bot.load_extension(f'comandos.{cog_name}')
        print(f'Cargando: {cog_name}')
      except Exception as e:
        print(f'Error al cargar {cog_name}: {e}')

async def main():
  await load()
  await bot.start(os.environ['TOKEN'])

keep_alive()
asyncio.run(main())