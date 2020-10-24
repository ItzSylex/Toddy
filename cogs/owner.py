import discord
from discord.ext import commands
from utils.database import Database

import aiosqlite
import asyncio
import os
import constants

import inspect
from utils.resources.custom_embed import CustomEmbed


class Owner(commands.Cog):
    """Commands only for the bot owner"""
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx) -> bool:
        """Makes sure only owner can run commands"""
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def reload(self, ctx, extension: str = None) -> None:
        """Reloads extension given"""

        cogs = os.listdir('./cogs')
        utils = os.listdir('./utils')

        if extension is None:
            for x, y in [(cogs, utils)]:
                for cog_file in cogs:
                    if cog_file.endswith('.py'):
                        if cog_file not in ["loops.py", "economy.py"]:
                            try:
                                self.bot.reload_extension(f'cogs.{cog_file[:-3]}')
                            except Exception as e:
                                raise e
                                await ctx.message.add_reaction(f"{constants.x}")
                for utils_file in utils:
                    if utils_file.endswith('.py'):
                        try:
                            self.bot.reload_extension(f'utils.{utils_file[:-3]}')
                        except Exception as e:
                            raise e
                            await ctx.message.add_reaction(f"{constants.x}")

            embed = discord.Embed(description = f"{constants.check} Listo el Reload.", color = constants.green)
            await ctx.send(embed = embed)
        else:
            try:
                self.bot.reload_extension(f'cogs.{extension}')
                embed = discord.Embed(description = f"{constants.check} Listo el Reload.", color = constants.green)
                await ctx.send(embed = embed)
            except Exception as e:
                raise e
                await ctx.message.add_reaction(f"{constants.x}")

    @commands.command()
    async def load_members(self, ctx, guild_id: int = None):
        if guild_id is None:
            for guild in self.bot.guilds:
                for member in guild.members:
                    if not await self.bot.dab.exists_db(member, guild):
                        await self.bot.db.execute(
                            """INSERT INTO users (
                                guild_id, user_id, mute, warns, guild_name
                            ) VALUES (?, ?, ?, ?, ?)""", (guild.id, member.id, 0, 0, guild.name)
                        )
            await self.bot.db.commit()
            await ctx.message.add_reaction(f"{constants.check}")

        else:
            guild = self.bot.get_guld(guild_id)
            for member in guild.members:
                if not await self.bot.dab.exists_db(member, guild):
                    await self.bot.db.execute(
                        """INSERT INTO users (
                            guild_id, user_id, mute, warns, guild_name
                        ) VALUES (?, ?, ?, ?, ?)""", (guild.id, member.id, 0, 0, guild.name)
                    )
            await self.bot.db.commit()
            await ctx.message.add_reaction(f"{constants.check}")


    async def if_not_insert(self, member):

        sql = """SELECT * FROM economy WHERE user_id = ?"""

        data = (member.id,)

        cursor = await self.bot.db.execute(sql, data)

        data = await cursor.fetchall()

        if len(data) == 0:
            query = """INSERT INTO economy(
                user_id, bank, wallet, inventory, pet, pet_name, pet_type, last_time_fed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            data_tuple = (member.id, 0, 0, "[]", 0, None, None, None)

            await self.bot.db.execute(query, data_tuple)
            await self.bot.db.commit()

    @commands.command(hidden = True)
    async def insert_economy(self, ctx):
        for guild in self.bot.guilds:
            for member in guild.members:
                await self.if_not_insert(member)

        await ctx.message.add_reaction(f"{constants.check}")

    @commands.command()
    async def insert_guilds(self, ctx):
        for guild in self.bot.guilds:
            await self.add_guild(guild)

        await ctx.message.add_reaction(f"{constants.check}")

    async def add_guild(self, guild):
        sql = """SELECT * FROM guilds WHERE guild_id = ?"""

        data = (guild.id,)

        cursor = await self.bot.db.execute(sql, data)

        data = await cursor.fetchall()

        if len(data) == 0:
            await self.bot.db.execute(
                """INSERT INTO guilds(
                    mod_roles, guild_id
                ) VALUES (?, ?)""", ("[]", guild.id)
            )
            await self.bot.db.commit()



def setup(bot):
    bot.add_cog(Owner(bot))
