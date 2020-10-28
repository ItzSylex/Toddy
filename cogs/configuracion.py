import discord
from discord.ext import commands

import constants
import config
import ast


class Configuracion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_list(self, action, guild_id, role_id):

        sql = """SELECT mod_roles FROM guilds WHERE guild_id = ?"""
        data_tuple = (guild_id,)
        cursor = await self.bot.db.execute(sql, data_tuple)
        data = await cursor.fetchone()
        role_config = ast.literal_eval(data[0])

        if action == "add":

            if role_id in role_config:
                return False

            role_config.append(role_id)

            sql = """UPDATE guilds SET mod_roles = ? WHERE guild_id = ?"""
            data_tuple = (str(role_config), guild_id)
            await self.bot.db.execute(sql, data_tuple)
            await self.bot.db.commit()

        if action == "remove":
            try:
                role_config.remove(role_id)
            except ValueError:
                return False

            sql = """UPDATE guilds SET mod_roles = ? WHERE guild_id = ?"""
            data_tuple = (str(role_config), guild_id)
            await self.bot.db.execute(sql, data_tuple)
            await self.bot.db.commit()

    @commands.command(
        brief = "Agrega un rol a la lista de roles permitidos para usar comandos de mod / admin",
        usage = f"{config.prefix}arol [rol]",
        aliases = ["agregarrol"]
    )
    @commands.has_permissions(administrator = True)
    async def arol(self, ctx, role: discord.Role = None):
        if role:
            result = await self.update_list("add", ctx.guild.id, role.id)

            if result is False:
                embed = discord.Embed(
                    description = f"{constants.x} Este rol **ya** está en la lista de roles permitidos.",
                    color = constants.red
                )
                return await ctx.send(embed = embed)

            embed = discord.Embed(
                description = f"{constants.check} El rol **{role.name}** ha sido agregado correctamente",
                color = constants.green
            )
            await ctx.send(embed = embed)

        else:
            embed = discord.Embed(
                description = f"{constants.x} Pon el ID o la mencion el rol que quieras agregar a la lista de roles de mod.",
                color = constants.red
            )
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Quita un rol de la lista de roles que pueden usar los comandos de mod / admin",
        usage = f"{config.prefix}qrol [rol]",
        aliases = ["quitarrol"]
    )
    @commands.has_permissions(administrator = True)
    async def qrol(self, ctx, role: discord.Role = None):
        if role:
            result = await self.update_list("remove", ctx.guild.id, role.id)

            if result is False:
                embed = discord.Embed(
                    description = f"{constants.x} Este rol **no** está en la lista de roles permitidos.",
                    color = constants.red
                )
                return await ctx.send(embed = embed)

            embed = discord.Embed(
                description = f"{constants.check} El rol **{role.name}** ha sido removido correctamente",
                color = constants.green
            )
            await ctx.send(embed = embed)

        else:
            embed = discord.Embed(
                description = f"{constants.x}Pon el ID o menciona el rol que quieras agregar a la lista de roles de mod.",
                color = constants.red
            )
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra todos los roles que tienen permisos para usar comandos de mod",
        usage = f"{config.prefix}lisrols"
    )
    async def lisrols(self, ctx):
        sql = """SELECT mod_roles FROM guilds WHERE guild_id = ?"""
        data_tuple = (ctx.guild.id,)
        cursor = await ctx.bot.db.execute(sql, data_tuple)
        data = await cursor.fetchone()
        role_config = ast.literal_eval(data[0])

        roles = [role.id for role in ctx.guild.roles]

        description = ""

        for role in role_config:
            if role in roles:
                role_obj = ctx.guild.get_role(role)
                description = description + f"ID: **{role_obj.id}** ► {role_obj.mention}\n"

        embed = discord.Embed(
            title = "Roles con permisos:",
            description = description if len(description) != 0 else "Aun no hay roles que pueden usar comandos de mod. Si tienes permisos de administrador, usa el comando `arol` para agregar roles.",
            color = constants.blue
        )
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Configuracion(bot))
