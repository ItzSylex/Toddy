import discord
import constants
from collections import Counter

from discord.ext import commands
import config
from datetime import datetime

import asyncio
import os
import random


class Info(commands.Cog):

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

        status = {}
        for each in ["mobile", "desktop", "web", None]:
            status.update({each: Counter(x.status for x in ctx.guild.members if each in x._client_status)})

        for x, y in status.items():
            if x is not None:
                await ctx.send(f"{x} and {y}")

        fields = [
            (
                "Miembros",
                f"Total: {members:,}\n{constants.online}Conectado: {statuses[0]}{constants.idle}Ausente{statuses[1]}\n{constants.dnd}No Molestar{statuses[2]}{constants.offline}Desconectado{statuses[3]}"
            )
        ]

        fields = [
            (
                "Miembros",
                f"Total: {members:,}\n Bots: {bots:,}\n Miembros {users:,}",
                True
            ),
            (
                "Canales",
                f"De texto: {len(ctx.guild.text_channels)}\nDe voz: {len(ctx.guild.voice_channels)}\nCategorias: {len(ctx.guild.categories)}",
                True
            ),
            (
                f"Estados",
                f"{constants.online}{statuses[0]}{constants.idle}{statuses[1]}\n{constants.dnd}{statuses[2]}{constants.offline}{statuses[3]}",
                False
            )
        ]

        embed = discord.Embed(
            title=f'Informacion de {ctx.guild.name}',
            description = f"**Owner**: \n ```\n{ctx.guild.owner.name}```"
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
            title = f"{member}'s Avatar",
            url = str(member.avatar_url),
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text = f"Pedido por {ctx.message.author}")
        embed.set_image(url = str(member.avatar_url))
        await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra informacion del usario",
        usage = f"{config.prefix}info",
        aliases = ["userinfo", "ui", "i"]
    )
    async def info(self, ctx, member: discord.Member = None):
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
            )

        ]

        for name, value, inline in fields:
            embed.add_field(
                name = name,
                value = value,
                inline = inline
            )

        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Info(bot))
