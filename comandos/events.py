import nextcord
from datetime import datetime
from nextcord.ext import commands

class Events(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.time = datetime.utcnow()

  @commands.Cog.listener()
  async def on_ready(self):
    print(f'Accediendo como: {self.bot.user}')
    await self.bot.change_presence(activity=nextcord.Game(name='Mejorando el sistema de registro de Royal bot'))

  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    print(f"Se unió al servidor: {guild.name} (ID: {guild.id})")
    channel = self.bot.get_channel(1198395146333606059)
    if channel:
        owner = guild.owner
        member_count = guild.member_count
        bot_count = sum(member.bot for member in guild.members)
        role_count = len(guild.roles)
        total_members = member_count + bot_count

        added_by = await self.get_added_by_info(guild)
        thumbnail_url = guild.icon.url

        message = (
            f"**Servidor**: {guild.name} (ID: {guild.id})\n"
            f"**Dueño:** {owner.name}#{owner.discriminator} (ID: {owner.id})\n"
            f"**Añadido por:** {added_by}\n"
            f"**Miembros:** {member_count}\n"
            f"**Bots:** {bot_count}\n"
            f"**Roles:** {role_count}"
        )

        embed = nextcord.Embed(
            title='¡Acabo de unirme a nuevo servidor!',
            description=message,
            color=nextcord.Color.blue(),
            timestamp=self.time
        )
        embed.set_thumbnail(url=thumbnail_url)  # Establecer el icono del servidor en el embed
        await channel.send(embed=embed)
    else:
      print(f"No se encontró el canal con ID 1198395146333606059 en el servidor {guild.name} (ID: {guild.id})")
    for channel in guild.text_channels:
      if channel.permissions_for(guild.me).send_messages:
        await channel.send(f"¡Hola! Gracias por invitarme a {guild.name}. Espero que disfrutes de mis comandos\nPara ver mis comandos coloca r/help.")
        break

  @commands.Cog.listener()
  async def on_guild_remove(self, guild):
    print(f"Fui expulsado del servidor: {guild.name} (ID: {guild.id})")
    channel = self.bot.get_channel(1198395146333606059)

    if channel:
        message = (
            f"**Servidor**: {guild.name} (ID: {guild.id})\n"

        )

        embed = nextcord.Embed(
            title='¡He sido expulsado de un servidor!',
            description=message,
            color=nextcord.Color.red(),
            timestamp=self.time
        )
        await channel.send(embed=embed)

  async def get_added_by_info(self, guild):
    invites = await guild.invites()
    
    for invite in invites:
      if invite.inviter.bot == False:
        return f"{invite.inviter.name}#{invite.inviter.discriminator} (ID: {invite.inviter.id})"
    
    return "No se pudo determinar quién añadió el bot"

async def setup(bot):
  bot.add_cog(Events(bot))