import discord
from discord.ext import commands

import constants
import config

import econstants
import random


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.shop = econstants.shop

    async def get_balance(self, member):
        sql = """SELECT wallet, bank FROM economy WHERE user_id = ?"""
        data = (member.id,)

        cursor = await self.bot.db.execute(sql, data)
        data = await cursor.fetchone()

        return data

    async def update_amount(self, member, amount, type):

        if type == "add":

            sql = """UPDATE economy SET wallet = wallet + ? WHERE user_id = ?"""
            data_tuple = (amount, member.id)

        if type == "subs":

            sql = """UPDATE economy SET wallet = wallet - ? WHERE user_id = ?"""
            data_tuple = (amount, member.id)

        await self.bot.db.execute(sql, data_tuple)
        await self.bot.db.commit()

    async def transaction(self, member, amount, type):
        if type == "to_bank":
            sql = """UPDATE economy SET wallet = wallet - ? AND bank = bank + ? WHERE user_id = ?"""
            data_tuple = (amount, amount, member.id)

        if type == "to_wallet":
            sql = """UPDATE economy SET wallet = wallet + ? AND bank = bank - ? WHERE user_id = ?"""
            data_tuple = (amount, amount, member.id)

        await self.bot.db.execute(sql, data_tuple)
        await self.bot.db.commit()

    async def gift(self, member, to, amount):
        pass

    @commands.command(
        brief = "Muestra el balance del usario",
        usage = f"{config.prefix}balance [usario]"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def balance(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        data = await self.get_balance(member)

        embed = discord.Embed(
            description = f"**Billetera:** {data[0]:,}\n**Banco:** {data[1]:,}\n**Total:** {data[0] + data[1]:,}",
            color = constants.blue
        )
        embed.set_author(name = str(ctx.author), icon_url = ctx.author.avatar_url)

        await ctx.send(embed = embed)

    @commands.command(
        brief = "Probabilidad de recibir una suma de dinero muy baja.",
        usage = f"{config.prefix}pedir"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def pedir(self, ctx):
        pass

    @commands.command(
        brief = "Busca en la basura, puede dar dinero, nada un item o una baja probabilidad de un pato dorado",
        usage = f"{config.prefix}buscar"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def buscar(self, ctx):
        rand_amount = random.randint(50, 100)
        chance = random.choices([rand_amount, 0, 1], weights = [.7, .3, .01])

        print(chance)
        print(rand_amount)

        if chance[0] == 0:
            discord.Embed(description = random.choice(econstants.NOTHING_RESPONSE))
        if chance[0] == 1:
            await self.update_amount(ctx.author, 5000, "add")
            await ctx.send(f"Encontraste un pato dorado y lo vendiste por **5,000** monedas")
        if chance[0] == rand_amount:
            await self.update_amount(ctx.author, rand_amount, "add")
            await ctx.send(f"Encontraste **{rand_amount:,}** monedas")

    @commands.command(
        brief = "Muestra todos los items que tiene el usuario.",
        usage = f"{config.prefix}inventario"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def inventario(self, ctx, member: discord.Member = None):
        pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for member in guild.members:
            await self.if_not_insert(member)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.if_not_insert(member)

    async def if_not_insert(self, member):

        sql = """SELECT * FROM economy WHERE user_id = ?"""

        data = (member.id,)

        cursor = await self.bot.db.execute(sql, data)

        data = await cursor.fetchall()

        if len(data) == 0:
            query = """INSERT INTO economy(
                user_id, bank, wallet, inventory, pet, pet_name, pet_type, last_time_fed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            data_tuple = (member.id, 0, 0, None, 0, None, None, None)

            await self.bot.db.execute(query, data_tuple)
            await self.bot.db.commit()


def setup(bot):
    bot.add_cog(Economy(bot))
