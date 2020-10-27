import discord
from discord.ext import commands

import constants

class Logger(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command is not None:

            cog = ctx.command.cog.qualified_name

            if ctx.guild.id == 75638384146723636:
                return

            channel = self.bot.get_channel(768260081657577482)

            embed = discord.Embed(
                description = f"{constants.check} Completed command **{ctx.command.name}** in **{ctx.guild.name}** by **{ctx.author}**",
                color = constants.green
            )

            if cog == "Moderacion":
                embed.color = constants.red
            if cog == "Varios":
                embed.color = constants.yellow

            await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(768318825527246870)

        embed = discord.Embed(description = f"{constants.check} Joined **{guild.name}**, heres the id: **{guild.id}**.\nOwner of the guild is **{guild.owner}**")

        await channel.send(embed = embed)





def setup(bot):
    bot.add_cog(Logger(bot))
