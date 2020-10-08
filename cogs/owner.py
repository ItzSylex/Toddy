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
                        if cog_file != "loops.py":
                            try:
                                self.bot.reload_extension(f'cogs.{cog_file[:-3]}')
                                await ctx.message.add_reaction(f"{constants.check}")
                            except Exception as e:
                                raise e
                                await ctx.message.add_reaction(f"{constants.x}")
                for utils_file in utils:
                    if utils_file.endswith('.py'):
                        try:
                            self.bot.reload_extension(f'utils.{utils_file[:-3]}')
                            await ctx.message.add_reaction(f"{constants.check}")
                        except Exception as e:
                            raise e
                            await ctx.message.add_reaction(f"{constants.x}")
        else:
            try:
                self.bot.reload_extension(f'cogs.{extension}')
                await ctx.message.add_reaction(f"{constants.check}")
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


def setup(bot):
    bot.add_cog(Owner(bot))
