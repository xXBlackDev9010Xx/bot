import nextcord
import sqlite3
from datetime import datetime
from nextcord.ext import commands
from pandas._libs.lib import indices_fast

def find_changes(before, after):
  changes = ''
  before_len, after_len = len(before), len(after)
  min_len = min(before_len, after_len)
  for i in range(min_len):
    if before[i] != after[i]:
      changes += after[i]
  
  if before_len > after_len:
    changes += before[after_len:]
  elif after_len > before_len:
    changes += after[before_len:]
  
  return changes

class Logs(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.db_connection = sqlite3.connect('./datos/logs.db')
    self.color = nextcord.Colour(0x7289DA)
    self.time = datetime.utcnow()
    self.create_table()

  def create_table(self):
    cursor = self.db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS log_channels (guild_id INTEGER, channel_id INTEGER)''')
    self.db_connection.commit()

  def save_log_channel(self, guild_id, channel_id):
    cursor = self.db_connection.cursor()
    cursor.execute('INSERT OR REPLACE INTO log_channels (guild_id, channel_id) VALUES (?, ?)', (guild_id, channel_id))
    self.db_connection.commit()
    

  def get_log_channel(self, guild_id):
    cursor = self.db_connection.cursor()
    cursor.execute('SELECT channel_id FROM log_channels WHERE guild_id = ?', (guild_id,))
    result = cursor.fetchone()
    return result[0] if result is not None else None
    

  @commands.command(help="Configura un canal de registro")
  async def setlog(self, ctx, channel: nextcord.TextChannel=None):
    if channel == None:
      return await ctx.send('Debes de mencionar un canal')
    self.save_log_channel(ctx.guild.id, channel.id)
    await ctx.send(f'El canal de logs se ha establecido en {channel.mention}')
      
  @commands.Cog.listener()
  async def on_message_delete(self, message):
    if message.author.bot:
      return
    log_channel_id = self.get_log_channel(message.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title="Contenido eliminado", color=self.color, timestamp=self.time)
        embed.add_field(name="Autor", value=message.author.mention, inline=False)
        embed.add_field(name="Contenido", value=message.content, inline=False)
        embed.add_field(name="Canal", value=message.channel.mention, inline=False)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
        embed.set_footer(text=f"ID del Contenido: {message.id}")
        await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_message_edit(self, message_before, message_after):
    if message_before.author.bot:
      return
    log_channel_id = self.get_log_channel(message_before.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if message_before.content != message_after.content:
        changes = find_changes(message_before.content, message_after.content)
        if log_channel:
          embed = nextcord.Embed(title='Contenido Editado', color=self.color, timestamp=self.time)
          embed.add_field(name="Autor", value=message_before.author.mention, inline=False)
          embed.add_field(name="Contenido Antes", value=message_before.content, inline=False)
          embed.add_field(name="Contenido Despues", value=message_after.content, inline=False)
          embed.add_field(name="Cambios", value=changes, inline=False)
          embed.add_field(name="Canal", value=message_before.channel.mention, inline=False)
          embed.set_author(name=message_before.author.display_name, icon_url=message_before.author.avatar.url)
          embed.set_footer(text=f'ID del Cotenido: {message_before.id}')
          await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_member_join(self, member):
    log_channel_id = self.get_log_channel(member.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title='Usuario Entrante', description=f'El usuario {member.mention} se ha unido al servidor.', color=self.color, timestamp=self.time)
        embed.set_author(name=member.display_name, icon_url=member.avatar.url)
        embed.set_footer(text=f'ID del Usuario: {member.id}')
        await log_channel.send(embed=embed)


  @commands.Cog.listener()
  async def on_member_remove(self, member):
    log_channel_id = self.get_log_channel(member.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title='Usuario Saliente', description=f'El usuario {member.mention} se ha ido del servidor.', color=self.color, timestamp=self.time)
        embed.set_author(name=member.display_name, icon_url=member.avatar.url)
        embed.set_footer(text=f'ID del Usuario: {member.id}')
        await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    log_channel_id = self.get_log_channel(before.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        if before.nick != after.nick:
          before_nick = before.nick if before.nick is not None else "None"
          after_nick = after.nick if after.nick is not None else "None"
          embed = nextcord.Embed(title='Nickname Actualizado', color=self.color, timestamp=self.time)
          embed.add_field(name='Antes', value=before.nick, inline=False)
          embed.add_field(name='Despues', value=after.nick, inline=False)
          embed.set_author(name=after.display_name, icon_url=after.avatar.url)
          embed.set_footer(text=f'ID del Usuario: {after.id}')
          await log_channel.send(embed=embed)
        elif before.roles != after.roles:
          added_roles = [role for role in after.roles if role not in before.roles]
          removed_roles = [role for role in before.roles if role not in after.roles]
          if added_roles:
            embed = nextcord.Embed(title='Roles Agregados', color=self.color, timestamp=self.time)
            embed.add_field(name='Usuario', value=after.mention, inline=False)
            embed.add_field(name='Roles Agregados', value=', '.join([role.mention for role in added_roles]), inline=False)
            embed.set_author(name=after.display_name, icon_url=after.avatar.url)
            embed.set_footer(text=f'ID del Usuario: {after.id}')
            await log_channel.send(embed=embed)
          if removed_roles:
            embed = nextcord.Embed(title='Roles Removidos', color=self.color, timestamp=self.time)
            embed.add_field(name='Usuario', value=after.mention, inline=False)
            embed.add_field(name='Roles Removidos', value=', '.join([role.mention for role in removed_roles]), inline=False)
            embed.set_author(name=after.display_name, icon_url=after.avatar.url)
            embed.set_footer(text=f'ID del Usuario: {after.id}')
            await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_channel_create(self, channel):
    log_channel_id = self.get_log_channel(channel.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title='Canal Creado', color=self.color, timestamp=self.time)
        embed.add_field(name='Nombre', value=channel.name, inline=False)
        embed.add_field(name='Creado por', value=channel.guild.get_member(channel.guild.owner_id).mention, inline=False)
        embed.add_field(name='Tipo', value=channel.type, inline=False)
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url)
        embed.set_footer(text=f'ID del Canal: {channel.id}')
        await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_channel_delete(self, channel):
    log_channel_id = self.get_log_channel(channel.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title='Canal Eliminado', color=self.color, timestamp=self.time)
        embed.add_field(name='Nombre', value=channel.name, inline=False)
        embed.add_field(name='Eliminado por', value=channel.guild.get_member(channel.guild.owner_id).mention, inline=False)
        embed.add_field(name='Tipo', value=channel.type, inline=False)
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url)
        embed.set_footer(text=f'ID del Canal: {channel.id}')
        await log_channel.send(embed=embed)
        
  @commands.Cog.listener()
  async def on_guild_channel_update(self, before, after):
    log_channel_id = self.get_log_channel(before.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        if before.name != after.name:
          embed = nextcord.Embed(title='Nombre de Canal Actualizado', color=self.color, timestamp=self.time)
          embed.add_field(name='Antes', value=before.name, inline=False)
          embed.add_field(name='Despues', value=after.name, inline=False)
          embed.set_author(name=after.guild.name, icon_url=after.guild.icon.url)
          embed.set_footer(text=f'ID del Canal: {after.id}')
          await log_channel.send(embed=embed)
        elif before.topic != after.topic:
          embed = nextcord.Embed(title='Tema de Canal Actualizado', color=self.color, timestamp=self.time)
          embed.add_field(name='Antes', value=before.topic, inline=False)
          embed.add_field(name='Despues', value=after.topic, inline=False)
          embed.set_author(name=after.guild.name, icon_url=after.guild.icon.url)
          embed.set_footer(text=f'ID del Canal: {after.id}')

  @commands.Cog.listener()
  async def on_guild_role_create(self, role):
    log_channel_id = self.get_log_channel(role.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title='Rol Creado', color=self.color, timestamp=self.time)
        embed.add_field(name='Nombre', value=role.name, inline=False)
        embed.add_field(name='Creado por', value=role.guild.get_member(role.guild.owner_id).mention, inline=False)
        embed.add_field(name='Color', value=role.color, inline=False)
        embed.set_author(name=role.guild.name, icon_url=role.guild.icon.url)
        embed.set_footer(text=f'ID del Rol: {role.id}')
        await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_role_delete(self, role):
    log_channel_id = self.get_log_channel(role.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        embed = nextcord.Embed(title='Rol Eliminado', color=self.color, timestamp=self.time)
        embed.add_field(name='Nombre', value=role.name, inline=False)
        embed.add_field(name='Eliminado por', value=role.guild.get_member(role.guild.owner_id).mention, inline=False)
        embed.set_author(name=role.guild.name, icon_url=role.guild.icon.url)
        embed.set_footer(text=f'ID del Rol: {role.id}')
        await log_channel.send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_role_update(self, before, after):
    log_channel_id = self.get_log_channel(before.guild.id)
    if log_channel_id is not None:
      log_channel = self.bot.get_channel(log_channel_id)
      if log_channel:
        if before.name != after.name:
          embed = nextcord.Embed(title='Nombre de Rol Actualizado', color=self.color, timestamp=self.time)
          embed.add_field(name='Antes', value=before.name, inline=False)
          embed.add_field(name='Despues', value=after.name, inline=False)
          embed.set_author(name=after.guild.name, icon_url=after.guild.icon.url)
          embed.set_footer(text=f'ID del Rol: {after.id}')
          await log_channel.send(embed=embed)
        elif before.color != after.color:
          embed = nextcord.Embed(title='Color de Rol Actualizado', color=self.color, timestamp=self.time)
          embed.add_field(name=f'Antes', value=before.color, inline=False)
          embed.add_field(name='Despues', value=after.color, inline=False)
          embed.set_author(name=after.guild.name, icon_url=after.guild.icon.url)
          embed.set_footer(text=f'ID del Rol: {after.id}')
          await log_channel.send(embed=embed)

async def setup(bot):
  bot.add_cog(Logs(bot))