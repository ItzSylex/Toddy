import discord
from discord.ext import commands

import constants

class Logger(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        channel = self.bot.get_channel(768260081657577482)

        embed = discord.Embed(
            description = f"{constants.check} Completed command **{ctx.command.name}** in **{ctx.guild.name}**",
            color = constants.green
        )
        await channel.send(embed = embed)

def setup(bot):
    bot.add_cog(Logger(bot))
