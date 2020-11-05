import discord
from discord.ext import commands
import constants


class ServerHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 756383841467236364:
            embed = discord.Embed(
                color = constants.blue,
                description = f"Bienvenido {member.mention}!"
            )
            embed.set_thumbnail(url = member.avatar_url)

            channel = self.bot.get_channel(773744967872413696)

            role = member.guild.get_role(769417726057644032)

            await member.add_roles(role)

            await channel.send(embed = embed)


def setup(bot):
    bot.add_cog(ServerHandler(bot))
