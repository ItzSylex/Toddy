import discord
import ast
from discord.ext import commands
from utils.resources.custom_errors import NoRequiredRole, NoSupplies


"""
11 muncion
2 rifle

12 cebo
10 Caña
"""


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


def has_item(**items):
    async def predicate(ctx):
        sql = """SELECT inventory FROM economy WHERE user_id = ?"""
        data = (ctx.author.id,)

        cursor = await ctx.bot.db.execute(sql, data)
        data = await cursor.fetchone()

        inventory = ast.literal_eval(data[0])

        for item in inventory:
            if items["main"] in item.keys() and items["second"] in item.keys():
                return True

        raise NoSupplies()

    return commands.check(predicate)
