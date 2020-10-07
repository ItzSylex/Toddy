import discord
from discord.ext import commands

import constants
from datetime import datetime

import config


class Informacion(commands.Cog):
    """
    Muestra informacion general sobre el bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief = "Muestra todos los comandos disponibles",
        name = "help", usage = f";;help"
    )
    async def help_(self, ctx, *, query: str = None):
        if not query:
            embed = discord.Embed(
                title = f'{constants.info} Lista de comandos.',
                description = f'Usa `{config.prefix}help [comando]` o `{config.prefix}help [categoria]` para mas informacion.',
                color = 0x02afe6
            )

            for name, cog in self.bot.cogs.items():
                if name == "Owner":
                    continue
                cmds_in_cog = ', '.join(["shh" if command.name == "hush" else command.name for command in cog.get_commands()])
                if len(cmds_in_cog) == 0:
                    pass
                else:
                    embed.add_field(name=f"{name}:", value = f"```ini\n[{cmds_in_cog}]```", inline=False)
            return await ctx.send(embed=embed)

        if query in self.bot.cogs.keys():
            cog = self.bot.get_cog(query)

            cmds_in_cog = ["shh" if command.name == "hush" else command.name for command in cog.get_commands()]

            embed = discord.Embed(
                title = f"{constants.info} {cog.qualified_name}",
                description = f"```ini\n[{cog.description}]```",
                color = 0x02afe6
            )
            embed.add_field(name='Comandos disponibles:', value = f"```ini\n[{', '.join(cmds_in_cog)}]```")
            return await ctx.send(embed=embed)

        possible_command = self.bot.get_command(query)

        if possible_command is None:
            return await ctx.send(f'{constants.x} No existe este comando. Usa `{config.prefix}help` para ver todos los comandos.')

        embed = discord.Embed(title=f'{constants.info} Informacion del comando `{possible_command.qualified_name}`', description = f"```ini\n[{possible_command.brief}]```", color = 0x02afe6)
        embed.add_field(name = "Ejemplo de uso:", value = f"```ini\n[{possible_command.usage}]```")
        embed.add_field(name = "Alias:", value = f"```ini\n{possible_command.aliases}```")

        await ctx.send(embed=embed)

    @commands.command(
        brief = "Muestra algunos detalles del bot",
        usage = ";;stats"
    )
    async def stats(self, ctx):
        embed = discord.Embed(
            title = f"{constants.info} Stats de Toddy:",
            color = 0x02afe6
        )
        embed.add_field(name = "Creador", value = f"```ini\n[.sylex#2803]```")
        embed.add_field(name = "Servidores", value = f"```ini\n [Estoy en {len(self.bot.guilds)} servidores]```")
        members = [guild.member_count for guild in self.bot.guilds]
        embed.add_field(name = "Usuarios", value = f"```ini\n[Viendo a {sum(members)} usuarios]```")
        cant = []
        for name, cog in self.bot.cogs.items():
            cmds = len([command.name for command in cog.get_commands()])
            cant.append(cmds)
        embed.add_field(name = "Cantidad de comandos", value = f"```ini\n[Hay {sum(cant)} comandos]```")
        embed.add_field(name = "Codigo", value = f"```ini\n[Escrito en Python]```")
        delta_uptime = datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed.add_field(name = "Tiempo en Linea", value = f"```ini\n[{days}d, {hours}h, {minutes}m]```")
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Informacion(bot))
