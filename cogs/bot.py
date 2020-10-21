import discord
from discord.ext import commands

import constants
from datetime import datetime

import config


class Bot(commands.Cog):
    """
    Muestra informacion general sobre el bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief = "Muestra todos los comandos disponibles",
        name = "help", usage = f";help"
    )
    async def help_(self, ctx, *, query: str = None):
        if not query:
            embed = discord.Embed(
                description = f'Usa `{config.prefix}help [comando]` o `{config.prefix}help [categoria]` para mas informacion.',
                color = 0x02afe6
            )
            file = discord.File("emotes/info_thumb.png", filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")

            for name, cog in self.bot.cogs.items():
                if name in ["Owner", "Jishaku"]:
                    continue
                cmds_in_cog = ', '.join(["shh" if command.name == "hush" else command.name for command in cog.get_commands()])
                if len(cmds_in_cog) == 0:
                    pass
                else:
                    embed.add_field(name=f"{name}:", value = f"```ini\n[{cmds_in_cog}]```", inline=False)
            return await ctx.send(file = file, embed = embed)

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

        embed = discord.Embed(title=f'{constants.info} Informacion del comando `{possible_command.qualified_name}`', description = f"{possible_command.brief}", color = 0x02afe6)
        embed.add_field(name = "Ejemplo de uso:", value = f"```ini\n[{possible_command.usage}]```")
        embed.add_field(name = "Alias:", value = f"```ini\n{possible_command.aliases}```")

        await ctx.send(embed=embed)

    @commands.command(
        brief = "Muestra algunos detalles del bot",
        usage = ";botinfo"
    )
    async def botinfo(self, ctx):
        embed = discord.Embed(
            title = f"{constants.info} Informacion de Toddy:",
            color = 0x02afe6,
            description = "Para **invitar** a Toddy [clickea aca](https://discord.com/api/oauth2/authorize?client_id=756377891264135249&permissions=8&scope=bot), asegurate de darle todos los permisos necesarios."
        )
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        members = [guild.member_count for guild in self.bot.guilds]
        cant = []
        for name, cog in self.bot.cogs.items():
            cmds = len([command.name for command in cog.get_commands()])
            cant.append(cmds)
        delta_uptime = datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed.add_field(name = "Cantidad de comandos", value = f"Tengo {sum(cant)} comandos", inline = False)
        embed.add_field(name = "Usuarios", value = f"Viendo a {sum(members)} usuarios", inline = False)
        embed.add_field(name = "Tiempo en Linea", value = f"{days}d, {hours}h, {minutes}m", inline = False)
        await ctx.send(embed = embed)

    @commands.command(
        brief = "Dar sugerencias para el bot",
        usage = f"{config.prefix}sugerencia [mensaje]",
        aliases = ["suggest", "reporte"]
    )
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def sugerencia(self, ctx, *, message):
        channel = self.bot.get_channel(765729594980433960)

        embed = discord.Embed(
            title = f"{constants.suggestion} Sugerencia nueva.",
            description = message,
            color = constants.blue
        )
        embed.add_field(name = "Servidor", value = f"Nombre: {ctx.guild.name}\nID: {ctx.guild.id}")
        embed.add_field(name = "Usuario", value = f"Nombre: {ctx.author}\nID: {ctx.author.id}\nApodo: {ctx.author.display_name}")
        await channel.send(embed = embed)
        await ctx.send(f"{constants.suggestion} Gracias por la sugerencia.")


def setup(bot):
    bot.add_cog(Bot(bot))
