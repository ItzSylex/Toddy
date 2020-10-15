from discord.ext import commands

import discord
import typing

import constants
import config
from utils.database import Database

import asyncio
import datetime

from utils.resources.custom_embed import CustomEmbed

# TODO: Add optional reason to Ban and Kick command


class Moderacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.seconds = {"m": 60, "h": 3600, "d": 86400}

    def convert_seconds(self, time):
        total = 0
        options = []

        for sub in time:
            if len(sub) == 1:
                return False
            else:
                for char in sub:
                    if char.isdigit() is False:
                        options.append(char)
        if all(opt.lower() in self.seconds.keys() for opt in options):
            for each in time:
                total = int(each[:-1]) * self.seconds[each[-1]] + total

            future_date = datetime.datetime.now() + datetime.timedelta(seconds = total)
            return future_date
        else:
            return False

    def same_level(self, author, target) -> bool:

        if isinstance(target, discord.Object):
            return False
        else:
            if all(getattr(obj, "top_role") for obj in [author, target]):
                if (
                    author.top_role == target.top_role or
                    target.guild_permissions.administrator or
                    target.guild_permissions.manage_roles or
                    target.guild_permissions.ban_members or
                    target.guild_permissions.kick_members
                ):
                    return True
                return False

    async def add_mute(self, ctx, member, role):

        embed = CustomEmbed(types = "mute", target = member).c()

        if await self.bot.dab.is_mute(member, ctx.guild):
            embed.description = f'{constants.check} {member.display_name} ya estaba silenciado antes.'
            return await ctx.send(embed = embed)

        else:
            await member.add_roles(role)
            await self.bot.db.execute(
                """UPDATE users SET mute = 1 WHERE guild_id = ? AND user_id = ?""", (ctx.guild.id, member.id)
            )
            await self.bot.db.commit()
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Silencia a un usuario", name = "mute",
        usage = f"{config.prefix}mute {constants.name}",
        aliases = ["m"]
    )
    @commands.check_any(
        commands.has_guild_permissions(administrator = True),
        commands.has_guild_permissions(manage_roles = True)
    )
    async def mute(self, ctx, member: discord.Member):

        mute_role = discord.utils.get(ctx.guild.roles, name = "Silenciado ❌")

        if self.same_level(ctx.author, member):
            embed = CustomEmbed(types = "error").c()
            return await ctx.send(embed = embed)

        if not mute_role:
            mute_role = await ctx.guild.create_role(name = 'Silenciado ❌', color = discord.Colour(0x666666))

            for channel in ctx.guild.channels:
                overwrites = channel.overwrites
                if isinstance(channel, discord.TextChannel):
                    overwrites[mute_role] = discord.PermissionOverwrite(send_messages = False, add_reactions = False)

                if isinstance(channel, discord.VoiceChannel):
                    overwrites[mute_role] = discord.PermissionOverwrite(speak = False)

                await channel.edit(overwrites = overwrites)

            await ctx.send(f"{constants.check} El rol Silenciado ha sido creado y los canales han sido editados", delete_after = 5.0)

            await self.add_mute(ctx, member, mute_role)

        else:
            await self.add_mute(ctx, member, mute_role)

    @commands.command(
        brief = "Quita el silencio de un usuario\n Para quitar el mute de alguien que no este en el servidor, usa su ID",
        name = "unmute", usage = f"{config.prefix}unmute {constants.name}",
        aliases = ["um"]
    )
    @commands.check_any(
        commands.has_guild_permissions(administrator = True),
        commands.has_guild_permissions(manage_roles = True)
    )
    async def unmute(self, ctx, member: typing.Union[discord.Member, discord.Object]):

        embed = CustomEmbed(types = "unmute", target = member).c()
        role = discord.utils.get(ctx.guild.roles, name = "Silenciado ❌")

        if await self.bot.dab.is_mute(member, ctx.guild):
            if isinstance(member, discord.Object):
                await self.bot.db.execute(
                    """UPDATE users SET mute = 0 WHERE guild_id = ? AND user_id = ?""", (ctx.guild.id, member.id)
                )
                await self.bot.db.commit()
            else:
                await member.remove_roles(role)
                await self.bot.db.execute(
                    """UPDATE users SET mute = 0 WHERE guild_id = ? AND user_id = ?""", (ctx.guild.id, member.id)
                )
                await self.bot.db.commit()

            return await ctx.send(embed = embed)
        else:
            embed.description = f'{constants.rwarn} {member.display_name} no esta silenciado.'
            embed.color = constants.red
            return await ctx.send(embed = embed)

    @commands.command(
        brief = "Banea a un usuario", name = "ban",
        usage = f"{config.prefix}ban {constants.name}",
        aliases = ["b"]
    )
    @commands.check_any(
        commands.has_permissions(administrator = True),
        commands.has_permissions(ban_members = True)
    )
    async def ban(self, ctx, member: typing.Union[discord.Member, discord.Object]):

        if self.same_level(ctx.author, member):
            embed = CustomEmbed(types = "error").c()
            return await ctx.send(embed = embed)
        else:
            await ctx.guild.ban(discord.Object(id = member.id), delete_message_days = 0)
            embed = CustomEmbed(types = "ban", target = member).c()
            return await ctx.send(embed = embed)

    @commands.command(
        brief = "Expulsa a un usuario del servidor",
        usage = f"{config.prefix}kick {constants.name}",
        aliases = ["k"]
    )
    @commands.check_any(
        commands.has_permissions(administrator = True),
        commands.has_permissions(kick_members = True)
    )
    async def kick(self, ctx, member: discord.Member):
        if self.same_level(ctx.author, member):
            embed = CustomEmbed(types = "error").c()
            return await ctx.send(embed = embed)
        else:
            await ctx.guild.kick(member)
            embed = CustomEmbed(types = "kick", target = member).c()
            return await ctx.send(embed = embed)

    @commands.command(
        brief = f"Quita el permiso para hablar en el canal. La cantidad de h's simboliza la cantidad de minutos.\nCada h equivale a 2 minutos, el maximo es de 15 minutos",
        usage = f"{config.prefix}shhhhhh",
        aliases = [],
        name = "hush"
    )
    @commands.check_any(
        commands.has_permissions(administrator = True),
        commands.has_permissions(manage_channels = True)
    )
    @commands.cooldown(rate = 1, per = 240, type = commands.BucketType.channel)
    async def silence(self, ctx, duration: int):
        if self.bot.eh_invoked is False:
            return
        else:

            query = "INSERT INTO c_mutes(channel_id, time_up, guild_id) VALUES (?, ?, ?)"

            when = datetime.datetime.now() + datetime.timedelta(minutes = duration)

            data_tuple = (ctx.channel.id, str(when), ctx.guild.id)

            await self.bot.db.execute(query, data_tuple)
            await self.bot.db.commit()

            loop_cog = self.bot.get_cog("Loops")
            current_mutes = loop_cog.current_mutes
            current_mutes[ctx.channel.id] = [str(when), ctx.guild.id]
            setattr(loop_cog, "current_mutes", current_mutes)

            overwrites = ctx.channel.overwrites
            self.bot.eh_invoked = False
            perm = ctx.channel.overwrites_for(ctx.guild.default_role)
            perm.send_messages = False
            overwrites[ctx.guild.default_role] = perm
            await ctx.channel.edit(overwrites = overwrites)
            embed = discord.Embed(description = f"{constants.check} {constants.mute}Silenciando canal por {duration} **minutos**", color = constants.green)
            await ctx.channel.send(embed = embed)

    @commands.command(
        brief = "Quita el silencio del canal",
        usage = f"{config.prefix}unshh",
        aliases = ["unsilence"],
        name = "unshh"
    )
    @commands.check_any(
        commands.has_permissions(administrator = True),
        commands.has_permissions(manage_channels = True)
    )
    async def _unsilence(self, ctx):
        loop = self.bot.get_cog("Loops")
        await loop.unmute_channel(ctx.channel.id, ctx.guild.id)

    @commands.command(
        brief = "Agrega una advertencia a el usario.",
        usage = f"{config.prefix}warn {constants.name} [razon opcional]",
        aliases = ["w"]
    )
    @commands.check_any(
        commands.has_permissions(administrator = True),
        commands.has_permissions(ban_members = True)
    )
    async def warn(self, ctx, member: discord.Member, *, reason = None):

        if self.same_level(ctx.author, member):
            embed = CustomEmbed(types = "error").c()
            return await ctx.send(embed = embed)

        query = """UPDATE users SET warns = warns + 1 WHERE user_id = ? AND guild_id = ?"""
        data_tuple = (member.id, ctx.guild.id)

        await self.bot.db.execute(query, data_tuple)
        await self.bot.db.commit()

        embed = CustomEmbed(types = "warn", target = member).c()
        return await ctx.send(embed = embed)

        if await self.bot.dab.is_max(member, member.guild):
            await ctx.guild.ban(discord.Object(id = member.id), delete_message_days = 0)
            await ctx.send(f'{constants.check} {member.display_name} ha sido baneado tras recibir 3 warns')

    @commands.command(
        brief = "Elimina una advertencia del usario.",
        usage = f"{config.prefix}unwarn {constants.name}",
        aliases = ["uw"]
    )
    @commands.check_any(
        commands.has_permissions(administrator = True),
        commands.has_permissions(ban_members = True)
    )
    async def unwarn(self, ctx, member: discord.Member):

        embed = CustomEmbed(types = "error").c()

        if self.same_level(ctx.author, member):
            return await ctx.send(embed = embed)

        if await self.bot.dab.is_zero(member, member.guild):
            embed.description = f"{constants.alert} {member.display_name} No tiene ningun warn."
            return await ctx.send(embed = embed)

        query = """UPDATE users SET warns = warns - 1 WHERE user_id = ? AND guild_id = ?"""
        data_tuple = (member.id, ctx.guild.id)

        await self.bot.db.execute(query, data_tuple)
        await self.bot.db.commit()

        embed = CustomEmbed(types = "unwarn", target = member).c()
        return await ctx.send(embed = embed)

    @commands.command(
        brief = "Silencia a un usario por un plazo de tiempo",
        usage = f"{config.prefix} tempmute 1d 2h 3m",
        aliases = ["tm", "tempm"]
    )
    @commands.check_any(
        commands.has_guild_permissions(administrator = True),
        commands.has_guild_permissions(manage_roles = True)
    )
    async def tempmute(self, ctx, member: discord.Member, *duration):
        if self.same_level(ctx.author, member):
            embed = CustomEmbed(types = "error").c()
            return await ctx.send(embed = embed)

        if duration and self.convert_seconds(duration) is not False:
            when = self.convert_seconds(duration)
            query = "INSERT INTO infractions(user_id, guild_id, time_up, type_inf) VALUES (?, ?, ?, ?)"
            data_tuple = (member.id, ctx.guild.id, str(when), "mute")

            await self.bot.db.execute(query, data_tuple)
            await self.bot.db.commit()

            loop_cog = self.bot.get_cog("Loops")
            current_infractions = loop_cog.current_infractions
            current_infractions[member.id] = [ctx.guild.id, str(when), "mute"]
            setattr(loop_cog, "current_infractions", current_infractions)

            role = discord.utils.get(ctx.guild.roles, name = "Silenciado ❌")
            await member.add_roles(role)

            embed = CustomEmbed(types = "tempmute", target = member).c()
            return await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = f'{constants.x}  Especifica el tiempo de la siguiente manera:',
                color = constants.red,
                description = "<numero>`d` | `h` | `m` |\nCada letra corresponde a; semanas, dias, horas, minutos, segundos\n\nEjemplo: ```ini\n[;;tempmute <miembro> 2d 3h]```"
            )
            return await ctx.send(embed = embed)

    @commands.command(
        brief = "Banea a un usario por un plazo de tiempo",
        usage = f"{config.prefix} tempban 1d 2h 3m",
        aliases = ["tb", "tempb"]
    )
    @commands.check_any(
        commands.has_guild_permissions(administrator = True),
        commands.has_guild_permissions(ban_members = True)
    )
    async def tempban(self, ctx, member: discord.Member, *duration):
        if self.same_level(ctx.author, member):
            embed = CustomEmbed(types = "error").c()
            return await ctx.send(embed = embed)

        if duration and self.convert_seconds(duration) is not False:
            when = self.convert_seconds(duration)
            query = "INSERT INTO infractions(user_id, guild_id, time_up, type_inf) VALUES (?, ?, ?, ?)"
            data_tuple = (member.id, ctx.guild.id, str(when), "ban")

            await self.bot.db.execute(query, data_tuple)
            await self.bot.db.commit()

            loop_cog = self.bot.get_cog("Loops")
            current_infractions = loop_cog.current_infractions
            current_infractions[member.id] = [ctx.guild.id, str(when), "ban"]
            setattr(loop_cog, "current_infractions", current_infractions)

            await ctx.guild.ban(discord.Object(id = member.id))

            embed = CustomEmbed(types = "tempban", target = member).c()
            return await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = f'{constants.x}  Especifica el tiempo de la siguiente manera:',
                color = constants.red,
                description = "<numero>`d` | `h` | `m` |\nCada letra corresponde a; semanas, dias, horas, minutos, segundos\n\nEjemplo: ```ini\n[;;tempmute <miembro> 2d 3h]```"
            )
            return await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Moderacion(bot))
