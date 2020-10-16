import discord
import random
import constants
from collections import Counter

from discord.ext import commands
import config
from datetime import datetime



class Varios(commands.Cog):

    """Comandos varios"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief = "Informacion acerca del servidor",
        usage = f"{config.prefix}serverinfo",
        aliases = ['sinfo'])
    @commands.guild_only()
    async def serverinfo(self, ctx):

        statuses = [
            len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
            len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
            len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
            len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))
        ]

        bans = len(await ctx.guild.bans())
        members = ctx.guild.member_count
        bots = len([member for member in ctx.guild.members if member.bot])
        users = len([member for member in ctx.guild.members if not member.bot])

        fields = [
            (
                f"Estados",
                f"{constants.online} Conectado: {statuses[0]:,}\n{constants.idle} Ausente: {statuses[1]:,}\n{constants.dnd} No Molestar: {statuses[2]:,}\n{constants.offline} Desconectado: {statuses[3]:,}",
                True
            ),
            (
                "Miembros",
                f"{constants.members} Total: {members:,}\n{constants.bots} Bots: {bots:,}\n{constants.members} Miembros {users:,}",
                True
            ),

            (
                "Canales",
                f"{constants.channel} De texto:{len(ctx.guild.text_channels)}\n{constants.voice} De voz: {len(ctx.guild.voice_channels)}",
                True
            )
        ]

        embed = discord.Embed(
            title = f'Informacion de {ctx.guild.name}',
            description = f"**Owner**: \n ```\n{ctx.guild.owner.name}```",
            color = constants.blue
        )
        embed.set_footer(text=f'Creado en | {ctx.guild.created_at.strftime("%b %d/%Y")}')
        embed.set_thumbnail(url=ctx.guild.icon_url)

        for name, value, inline in fields:
            embed.add_field(
                name = name,
                value = value,
                inline = inline
            )
        await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra el avatar de un usuario",
        usage = f"{config.prefix}avatar",
        aliases = ['a', 'pfp'])
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        embed = discord.Embed(
            title = f"Avatar de {member}",
            url = member.avatar_url,
            timestamp = datetime.utcnow(),
            color = constants.blue
        )
        embed.set_footer(text = f"Pedido por {ctx.message.author}")
        embed.set_image(url = member.avatar_url)
        await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra informacion del usario",
        usage = f"{config.prefix}info",
        aliases = ["info", "ui", "i"]
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        created_at = member.created_at.strftime('%B %d, %Y')
        joined_at = member.joined_at.strftime('%B %d, %Y')

        embed = discord.Embed(
            title = f"Informacion de {member}",
        )
        embed.set_thumbnail(url = member.avatar_url)
        roles = [role.mention if role.name != "@everyone" else "@everyone" for role in member.roles]
        embed.color = member.top_role.color if len(roles) != 1 else constants.blue
        roles = roles[1:] if len(roles) != 1 else roles
        roles = ", ".join(roles)

        statuses = [discord.Status.idle, discord.Status.online, discord.Status.dnd]

        top_role = member.top_role.mention if member.top_role.name != "@everyone" else "@everyone"

        sql = """SELECT warns FROM users WHERE user_id = ? AND guild_id = ?"""

        data = (member.id, ctx.guild.id)

        cursor = await self.bot.db.execute(sql, data)
        warns = await cursor.fetchone()

        fields = [
            (
                "ID:",
                member.id,
                True
            ),
            (
                "Apodo:",
                "No tiene" if member.nick is None else member.nick,
                True
            ),
            (
                "Cuenta creada:",
                created_at,
                True
            ),
            (
                "Informacion de Server",
                f"Se unio en: {joined_at}\nTop Rol: {top_role}\nRoles:\n{roles}",
                False
            ),
            (
                "Infracciones",
                f"Warns: {warns[0]}",
                False
            )

        ]

        for name, value, inline in fields:
            embed.add_field(
                name = name,
                value = value,
                inline = inline
            )

        await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra el ultimo mensaje borrado",
        usage = f"{config.prefix}snipe"
    )
    async def snipe(self, ctx, option = None):
        if option is None:
            try:
                message = self.bot.snipe[ctx.channel.id]
            except KeyError:
                return await ctx.send("No hay nada que ver aca")
            embed = discord.Embed(
                description = message.content,
                color = constants.blue,
                timestamp = message.created_at
            )
            embed.set_author(name = str(message.author), icon_url = message.author.avatar_url)
            del self.bot.snipe[ctx.channel.id]
            await ctx.send(embed = embed)
        if option.lower() == "edit":
            try:
                list_message = self.bot.snipe_edit[ctx.channel.id]
            except KeyError:
                return await ctx.send("No hay nada que ver aca")
            embed = discord.Embed(
                description = f"**Antes:** {list_message[0].content}\n**Despues:** {list_message[1].content}",
                color = constants.blue,
                timestamp = list_message[1].created_at
            )
            embed.set_author(name = str(list_message[1].author), icon_url = list_message[1].author.avatar_url)
            del self.bot.snipe_edit[ctx.channel.id]
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Respondo si o no a una pregunta",
        usage = f"{config.prefix}8ball [pregunta]",
        aliases = ["pregunta", "p", "8b"],
        name = "8ball"
    )
    async def _8ball(self, ctx, *, message):
        if message:
            respuesta = random.choice([f"Si. {constants.check}", f"No. {constants.x}"])
            await ctx.send(respuesta)
        else:
            await ctx.send("Umm")

    @commands.command(
        brief = "Agrega un emoji aplaudiendo entre cada palabra",
        usage = f"{config.prefix}clap [frase]"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clap(self, ctx, *, message):

        message = message.replace(" ", f" 👏 ")

        if len(message) >= 1200:
            return await ctx.send("Este mensaje es muy largo :(")

        await ctx.message.delete()
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Varios(bot))
