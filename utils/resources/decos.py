import discord
import ast
from discord.ext import commands
from utils.resources.custom_errors import NoRequiredRole


def is_mod():
    async def predicate(ctx):

        if not ctx.guild:
            return False

        else:
            if ctx.author.id == ctx.guild.owner.id:
                return True

            if ctx.author.guild_permissions.administrator:
                return True

            roles = [r.id for r in ctx.author.roles]

            sql = """SELECT mod_roles FROM guilds WHERE guild_id = ?"""
            data_tuple = (ctx.guild.id,)
            cursor = await ctx.bot.db.execute(sql, data_tuple)
            data = await cursor.fetchone()
            role_config = ast.literal_eval(data[0])

            if any(role in roles for role in role_config):
                return True

            raise NoRequiredRole()

    return commands.check(predicate)
