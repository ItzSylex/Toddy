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
        self.should_unumte.start()
        self.bot.loop.create_task(self.cache_mutes())
        self.current_mutes = {}

    async def cache_mutes(self):
        await self.bot.wait_until_ready()
        cursor = await self.bot.db.execute(
            """SELECT * FROM c_mutes"""
        )
        mutes = await cursor.fetchall()

        if mutes:
            muted_channels = {}
            for mute in mutes:
                muted_channels[mute[0]] = [mute[1], mute[2]]

                self.current_mutes = muted_channels

                pp.pprint(self.current_mutes)

    @tasks.loop(seconds = 1)
    async def should_unumte(self):
        await self.bot.wait_until_ready()

        if hasattr(self, "current_mutes"):

            for channel_id, details in list(self.current_mutes.items()):
                guild_id = details[1]
                time_to_unmute = d.strptime(details[0], '%Y-%m-%d %H:%M:%S.%f')

                if d.now() >= time_to_unmute:
                    await self.unmute_channel(channel_id, guild_id)

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

        await channel.send(
            f"{constants.check} Este canal ya no esta silenciado"
        )


def setup(bot):
    bot.add_cog(Loops(bot))
