from discord.ext import commands
import discord

import aiosqlite


class Database(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.conn())

    async def conn(self) -> None:
        """Makes database connection to users data base"""
        self.bot.db = await aiosqlite.connect('database.db')

    async def exists_db(self, member: discord.Member, guild: discord.Guild) -> bool:
        """Checks if the user is in the database"""
        if hasattr(member, 'id') and hasattr(guild, "id"):
            cursor = await self.bot.db.execute(
                'SELECT * FROM users WHERE user_id = ? AND guild_id = ?', (member.id, guild.id)
            )
            results = await cursor.fetchall()
            if len(results) > 0:
                return True
        return False

    async def is_mute(self, member: discord.Member, guild: discord.Guild) -> bool:
        """Checks if the user is currently muted"""
        if hasattr(member, 'id') and hasattr(guild, "id"):
            cursor = await self.bot.db.execute(
                'SELECT mute FROM users WHERE user_id = ? AND guild_id = ?', (member.id, guild.id)
            )
            results = await cursor.fetchone()
            if results[0] == 1:
                return True
        return False

    async def is_zero(self, member: discord.Member, guild: discord.Guild) -> bool:
        """Checks if active warns is 0"""
        if hasattr(member, 'id'):
            cursor = await self.bot.db.execute(
                'SELECT warns FROM users WHERE user_id = ? AND guild_id = ?', (member.id, guild.id)
            )
            results = await cursor.fetchone()
            if results[0] == 0:
                return True
        return False

    async def is_max(self, member: discord.Member, guild: discord.Guild) -> bool:
        """Checks if active warns is 3"""
        if hasattr(member, 'id'):
            cursor = await self.bot.db.execute(
                'SELECT warns FROM users WHERE user_id = ? AND guild_id = ?', (member.id, guild.id)
            )
            results = await cursor.fetchone()
            if results[0] == 3:
                return True
        return False


def setup(bot) -> None:
    """Loads Database Cog"""
    bot.add_cog(Database(bot))
