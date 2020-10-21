import discord
from discord.ext import commands

import constants

class Logger(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.guild.id == 756383841467236364:
            return

        channel = self.bot.get_channel(768260081657577482)

        embed = discord.Embed(
            description = f"{constants.check} Completed command **{ctx.command.name}** in **{ctx.guild.name}**",
            color = constants.green
        )
        await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(768318825527246870)

        embed = discord.Embed(description = f"{constants.check} Joined **{guild.name}**, heres the id: **{guild.id}**.\nOwner of the guild is **{guild.owner}**")

        await channel.send(embed = embed)





def setup(bot):
    bot.add_cog(Logger(bot))
