import discord
from discord.ext import commands

import aiosqlite
from utils.database import Database


## TODO: TEST on_member_join

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dab = Database(self.bot)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Added to a new server

        Will loop tru all the members and check if they exist with the
        specific guild id since users can be in multiple servers at once

        """

        for member in guild.members:
            if not await self.dab.exists_db(member, guild):
                await self.bot.db.execute(
                    """INSERT INTO users (
                        guild_id, user_id, mute, warns, guild_name
                    ) VALUES (?, ?, ?, ?, ?)""", (guild.id, member.id, 0, 0, guild.name)
                )
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        New member joins

        Should check if exists on database, if it does, check if its muted
        to add role, if its not on the database, add with its guild and user id

        """

        if not await self.dab.exists_db(member, member.guild):
            await self.bot.db.execute(
                    """INSERT INTO users (
                        guild_id, user_id, mute, warns, guild_name
                    ) VALUES (?, ?, ?, ?, ?)""", (guild.id, member.id, 0, 0, guild.name)
                )

        else:
            if await self.dab.is_mute(member, member.guild):
                mute_role = discord.utils.get(member.guild.roles, name =  "Silenciado ❌")

                if not mute_role:
                    await  member.guild.create_role(name = 'Silenciado ❌', color = discord.Colour(0x666666))

                    for channel in ctx.guild.channels:
                        overwrites =  channel.overwrites
                        if isinstance(channel, discord.TextChannel):
                            overwrites[mute_role] = discord.PermissionOverwrite(send_messages = False, add_reactions = False)

                        if isinstance(channel, discord.VoiceChannel):
                            overwrites[mute_role] = discord.PermissionOverwrite(speak = False)

                        await channel.edit(overwrites = overwrites)

                    await member.add_roles(mute_role, reason = "Rol dado al unirse por infraccion previa")
                else:
                    await member.add_roles(mute_role, reason = "Rol dado al unirse por infraccion previa")




def setup(bot):
    bot.add_cog(Events(bot))
