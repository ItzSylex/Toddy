import discord
from discord.ext import commands
import constants
import config

## TODO: REGEX TO MAKE SURE ONLY ANY AMOUNT OF X

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.eh_invoked = False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Triggers whenever there is an error"""


        if hasattr(ctx.command, 'on_error'):
            return

        skip = (commands.BadArgument, )

        error = getattr(error, 'original', error)

        # if isinstance(error, skip):
        #     return

        if isinstance(error, commands.CommandNotFound):
            invoked = ctx.invoked_with
            if invoked[0].lower() == "s":
                for char in invoked[1:]:
                    if char.lower() != "h":
                        return
                shh_command = self.bot.get_command("shh")
                self.bot.eh_invoked = True

                duration = invoked.count("h") * 1

                await ctx.invoke(shh_command, duration if duration <= 15 else 15)

        else:
            raise error











def setup(bot):
    bot.add_cog(ErrorHandler(bot))
