from discord.ext import commands, tasks
from datetime import datetime as d

import asyncio
import discord

import constants
import pprint

pp = pprint.PrettyPrinter(indent=4)


class Loops(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.cache_values())

        self.should_unumte.start()

        self.current_mutes = {}
        self.current_infractions = {}

    async def cache_values(self):
        await self.bot.wait_until_ready()

        self.bot.dab = self.bot.get_cog("Database")

        cursor_m = await self.bot.db.execute(
            """SELECT * FROM c_mutes"""
        )
        mutes = await cursor_m.fetchall()

        if mutes:
            muted_channels = {}
            for mute in mutes:
                muted_channels[mute[0]] = [mute[1], mute[2]]

                self.current_mutes = muted_channels

        cursor_in = await self.bot.db.execute(
            """SELECT * FROM infractions"""
        )

        infractions = await cursor_in.fetchall()

        if infractions:
            current_infractions = {}
            for infraction in infractions:
                current_infractions[infraction[0]] = [infraction[1], infraction[2], infraction[3]]

                self.current_infractions = current_infractions

    @tasks.loop(seconds = 1)
    async def should_unumte(self):
        await self.bot.wait_until_ready()

        if hasattr(self, "current_mutes"):

            for channel_id, details in list(self.current_mutes.items()):
                guild_id = details[1]
                time_to_unmute = d.strptime(details[0], '%Y-%m-%d %H:%M:%S.%f')

                if d.now() >= time_to_unmute:
                    await self.unmute_channel(channel_id, guild_id)

        if hasattr(self, "current_infractions"):
            for user_id, details_inf in list(self.current_infractions.items()):
                guild_id = details_inf[0]
                remove_time = d.strptime(details_inf[1], '%Y-%m-%d %H:%M:%S.%f')

                if d.now() >= remove_time:
                    await self.remove_infraction(user_id, guild_id, details_inf[2])

    async def unmute_channel(self, channel_id: int, guild_id: int):
        """
        Removes channel from cache,
        changes permissions to speak and updates database
        """

        del self.current_mutes[channel_id]

        query = """DELETE FROM c_mutes WHERE channel_id = ?"""

        data_tuple = (channel_id,)

        await self.bot.db.execute(query, data_tuple)
        await self.bot.db.commit()

        channel = self.bot.get_channel(channel_id)
        overwrites = channel.overwrites

        perm = channel.overwrites_for(channel.guild.default_role)
        perm.send_messages = True
        overwrites[channel.guild.default_role] = perm

        await channel.edit(overwrites = overwrites)

        embed = discord.Embed(description = f"{constants.check} {constants.unmute} Este canal ya no esta silenciado.", color = constants.green)
        await channel.send(embed = embed)

    async def remove_infraction(self, user_id: int, guild_id: int, inf_type: str):
        guild = self.bot.get_guild(guild_id)
        user = guild.get_member(user_id)

        del self.current_infractions[user_id]

        query = """DELETE FROM infractions WHERE user_id = ? AND guild_id = ?"""
        data_tuple = (user_id, guild_id)

        await self.bot.db.execute(
            """UPDATE users SET mute = 0 WHERE guild_id = ? AND user_id = ?""", (guild_id, user_id)
        )
        await self.bot.db.execute(query, data_tuple)
        await self.bot.db.commit()

        if user is not None:

            if inf_type == "ban":
                await guild.unban(discord.Object(id = user_id))

            if inf_type == "mute":
                embed = discord.Embed(description = f"{constants.check} Tu silencio en {guild.name} ha **terminado**.")
                try:
                    await user.send(embed = embed)
                except Exception:
                    pass
                finally:
                    role = discord.utils.get(guild.roles, name = "Silenciado ❌")
                    await user.remove_roles(role)


def setup(bot):
    bot.add_cog(Loops(bot))
