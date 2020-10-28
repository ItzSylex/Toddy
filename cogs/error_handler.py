import discord
from discord.ext import commands
import constants
import config
import ast
from utils.resources import custom_errors


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

        if isinstance(error, custom_errors.NoRequiredRole):
            embed = discord.Embed(
                description = f"{constants.x} No tienes los roles necesarios para usar este comando.",
                color = constants.red
            )
            return await ctx.send(embed = embed)

        if isinstance(error, commands.CommandNotFound):
            invoked = ctx.invoked_with
            if invoked[0].lower() == "s":
                for char in invoked[1:]:
                    if char.lower() != "h":
                        return

                sql = """SELECT mod_roles FROM guilds WHERE guild_id = ?"""
                data_tuple = (ctx.guild.id,)
                cursor = await ctx.bot.db.execute(sql, data_tuple)
                data = await cursor.fetchone()
                role_config = ast.literal_eval(data[0])
                roles = [r.id for r in ctx.author.roles]

                if any(role in roles for role in role_config) or ctx.author.guild_permissions.administrator:

                    shh_command = self.bot.get_command("hush")
                    self.bot.eh_invoked = True

                    duration = invoked.count("h") * 2

                    await ctx.invoke(shh_command, duration if duration <= 15 else 15)
                    return
                else:
                    embed = discord.Embed(
                        description = f"{constants.x} No tienes los roles necesarios para usar este comando.",
                        color = constants.red
                    )
                    return await ctx.send(embed = embed)
            else:
                return

        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "member":
                embed = CustomEmbed(types = "missing").c()
                await ctx.send(embed = embed)

        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description = f"{constants.x} Parece que me hacen falta ciertos permisos. Asegurate que tenga {error.missing_perms}",
                color = constants.red
            )
            await ctx.send(embed = embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description = f"{constants.x} No tienes los permisos necesarios para usar este comando.",
                color = constants.red
                )
            await ctx.send(embed = embed)

        else:
            raise error

    async def report(self, ctx, error):
        channel = self.bot.get_channel(768253649838407680)
        embed = discord.Embed(
            title = "Unexpected Error",
            description = f"```py\n{error}```",
            color = constants.red
        )
        embed.add_field(name = "Guild", value = f"{ctx.guild}\n{ctx.guild.id}")
        embed.add_field(name = "Comando", value = f"{ctx.command.name}")
        embed.add_field(name = "Usuario", value = f"{ctx.author}")
        await channel.send(embed = embed)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
