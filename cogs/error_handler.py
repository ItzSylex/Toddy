import discord
from discord.ext import commands
import constants
import config


from utils.resources.custom_embed import CustomEmbed


class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.eh_invoked = False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        skip = (commands.BadArgument, commands.CommandOnCooldown)

        error = getattr(error, 'original', error)

        if isinstance(error, skip):
            return

        if isinstance(error, commands.CommandNotFound):
            invoked = ctx.invoked_with
            if invoked[0].lower() == "s":
                for char in invoked[1:]:
                    if char.lower() != "h":
                        return
                shh_command = self.bot.get_command("hush")
                self.bot.eh_invoked = True

                duration = invoked.count("h") * 2

                await ctx.invoke(shh_command, duration if duration <= 15 else 15)

        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "member":
                embed = CustomEmbed(types = "missing").c()
                await ctx.send(embed = embed)
        else:
            raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
