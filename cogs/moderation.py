from discord.ext import commands

import discord
import typing

import constants
import config
from utils.database import Database

import asyncio
import datetime


# TODO: Add optional reason to Ban and Kick command

class Moderacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dab = Database(bot)

    def same_level(self, author, target) -> bool:
        """
        Helper function, checks if the target on commands like
        ban, mute, kick have permissions that should not make it possible
        to recieve the infraction
        """
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

        """
        Helper function that applies mute
        """

        embed = discord.Embed(
            title = f'{constants.check} {member.display_name} fue silenciado',
            color = constants.green
        )
        embed.add_field(name = "Mod / Admin:", value = ctx.author.display_name)
        embed.add_field(name = "ID del usuario:", value = member.id)

        if await self.dab.is_mute(member, ctx.guild):
            embed = discord.Embed(
                title = f'{constants.check} {member.display_name} ya estaba silenciado antes.',
                color = constants.green
            )
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
    async def mute(self, ctx, member: discord.Member = None):
        """
        Mutes an user by adding a role, if the role does not exists
        it creates it and set the corresponding overwrites
        """

        mute_role = discord.utils.get(ctx.guild.roles, name = "Silenciado ❌")

        if member is None:
            embed = discord.Embed(
                title = f'{constants.x}  Debes mencionar a alguien',
                color = constants.red
            )
            return await ctx.send(embed = embed, delete_after = 5.0)

        if self.same_level(ctx.author, member):
            embed = discord.Embed(
                title = f'{constants.x}  No puedo silenciar a este usario.',
                color = constants.red
            )
            return await ctx.send(embed = embed, delete_after = 5.0)

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
        brief = "Quita el silencio de un usuario",
        name = "unmute", usage = f"{config.prefix}unmute {constants.name}",
        aliases = ["um"]
    )
    @commands.check_any(
        commands.has_guild_permissions(administrator = True),
        commands.has_guild_permissions(manage_roles = True)
    )
    async def unmute(self, ctx, member: typing.Union[discord.Member, discord.Object] = None):

        """
        Unmutes the user by removing the role
        """

        embed = discord.Embed()
        role = discord.utils.get(ctx.guild.roles, name = "Silenciado ❌")
        embed.title = f'{constants.check} {member.display_name} ya no esta silenciado.'
        embed.color = constants.green
        embed.add_field(name = "Mod / Admin:", value = ctx.author.display_name)
        embed.add_field(name = "ID del usuario:", value = member.id)

        if member is not None:
            if await self.dab.is_mute(member, ctx.guild):
                if isinstance(member, discord.Object):
                    embed.title = f'{constants.check} {member.id} ya no esta silenciado.'
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
                embed.title = f'{constants.rwarn} {member.display_name} no esta silenciado.'
                embed.color = constants.red
                return await ctx.send(embed = embed)

        else:
            embed.title = f'{constants.x}  Debes mencionar a alguien'
            embed.color = constants.red
            return await ctx.send(embed = embed, delete_after = 5.0)

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
        embed = discord.Embed()
        embed.add_field(name = "Mod / Admin:", value = ctx.author.display_name)
        embed.add_field(name = "ID del usuario:", value = member.id)
        if self.same_level(ctx.author, member):
            embed = discord.Embed(
                title = f'{constants.x}  No puedo banear a este usario.',
                color = constants.red
            )
            return await ctx.send(embed = embed, delete_after = 5.0)
        else:
            try:
                await ctx.guild.ban(member, delete_message_days = 0)
            except Exception as e:
                raise e
                await ctx.guild.ban(discord.Object(id = member.id), delete_message_days = 0)
            finally:
                if isinstance(member, discord.Object):
                    embed.title = f'{constants.check} {member.id} ha sido baneado'
                    embed.color = constants.green
                else:
                    embed.title = f'{constants.check} {member.display_name} ha sido baneado'
                    embed.color = constants.green
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
            embed = discord.Embed(
                title = f'{constants.x}  No puedo expulsar a este usario.',
                color = constants.red
            )
            return await ctx.send(embed = embed, delete_after = 5.0)
        else:
            await ctx.guild.kick(member)
            embed = discord.Embed(
                title = f'{constants.check} {member.display_name} ha sido expulsado',
                color = constants.green
            )
            embed.add_field(name = "Mod / Admin:", value = ctx.author.display_name)
            embed.add_field(name = "ID del usuario:", value = member.id)
            return await ctx.send(embed = embed)

    @commands.command(
        brief = f"Quita el permiso para hablar en el canal. La cantidad de h's simboliza la cantidad de minutos.\nCada h equivale a 2 minutos, el maximo es de 15 minutos",
        usage = f"{config.prefix}shhhhhh",
        aliases = [],
        name = "shh"
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

            """
            We update our database and update the cache on the current muted channels
            """

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
            await ctx.channel.send(f"{constants.check} Silenciando canal por {duration} minutos")

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

        embed = discord.Embed()

        if self.same_level(ctx.author, member):
            embed.title = f'{constants.x}  No puedo darle warn a este usario.'
            embed.color = constants.red
            return await ctx.send(embed = embed, delete_after = 5.0)

        reason = "Razon no especificada" if reason is None else reason

        query = """UPDATE users SET warns = warns + 1 WHERE user_id = ? AND guild_id = ?"""
        data_tuple = (member.id, ctx.guild.id)

        await self.bot.db.execute(query, data_tuple)
        await self.bot.db.commit()

        if await self.dab.is_max(member, member.guild):
            await ctx.guild.ban(discord.Object(id = member.id), delete_message_days = 0)
            await ctx.send(f'{constants.check} {member} ha sido baneado tras recibir 3 warns')

        else:
            embed.title = f'{constants.check} {member.display_name} ha recibido un warn'
            embed.color = constants.green
            embed.description = f"Razon del warn:\n```ini\n[{reason}]```"
            embed.add_field(name = "Mod / Admin:", value = ctx.author.display_name)
            embed.add_field(name = "ID del usuario:", value = member.id)
            await ctx.send(embed = embed)

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
        embed = discord.Embed()

        if self.same_level(ctx.author, member):
            embed.title = f'{constants.x}  No puedo quitarle un warn a este usario.'
            embed.color = constants.red
            return await ctx.send(embed = embed, delete_after = 5.0)

        if await self.dab.is_zero(member, member.guild):
            embed.title = f'{constants.x}  No puedo quitarle un warn a este usario.'
            embed.color = constants.red
            embed.description = "No tiene ningun warn"
            return await ctx.send(embed = embed, delete_after = 5.0)

        query = """UPDATE users SET warns = warns - 1 WHERE user_id = ? AND guild_id = ?"""
        data_tuple = (member.id, ctx.guild.id)

        await self.bot.db.execute(query, data_tuple)
        await self.bot.db.commit()

        embed.title = f'{constants.check}  Warn de {member.display_name} removido'
        embed.color = constants.green
        embed.add_field(name = "Mod / Admin:", value = ctx.author.display_name)
        embed.add_field(name = "ID del usuario:", value = member.id)
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Moderacion(bot))
