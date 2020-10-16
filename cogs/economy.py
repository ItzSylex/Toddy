import discord
from discord.ext import commands, tasks

import constants
import config

import econstants
import random
import datetime


class Economia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.shop = random.sample(econstants.shop, 6)
        self.last_time_shop = datetime.datetime.now()
        self.update_shop.start()

    @tasks.loop(seconds = 2)
    async def update_shop(self):
        result = datetime.datetime.now() - self.last_time_shop
        print(result.total_seconds())
        if result.total_seconds() >= 14400:
            self.shop = random.sample(econstants.shop, 6)
            self.last_time_shop = datetime.datetime.now()

    async def get_balance(self, member):
        sql = """SELECT wallet, bank FROM economy WHERE user_id = ?"""
        data = (member.id,)

        cursor = await self.bot.db.execute(sql, data)
        data = await cursor.fetchone()

        return data

    async def update_amount(self, member, amount, tipo):

        if tipo == "add":

            sql = """UPDATE economy SET wallet = wallet + ? WHERE user_id = ?"""
            data_tuple = (amount, member.id)

        if tipo == "subs":

            sql = """UPDATE economy SET wallet = wallet - ? WHERE user_id = ?"""
            data_tuple = (amount, member.id)

        await self.bot.db.execute(sql, data_tuple)
        await self.bot.db.commit()

    async def transaction(self, member, amount, tipo):

        try:
            amount = int(amount)
        except ValueError:
            return 3
        else:
            data = await self.get_balance(member)

            if tipo == "to_bank":

                if data[0] >= amount:
                    total = data[1] + amount
                    remaining = data[0] - amount

                    sql = """UPDATE economy SET wallet = ?, bank = ? WHERE user_id = ?"""
                    data_tuple = (remaining, total, member.id)
                else:
                    return False

            if tipo == "to_wallet":

                if data[1] >= amount:
                    new_bank = data[1] - amount
                    new_wallet = data[0] + amount
                    sql = """UPDATE economy SET wallet = ?, bank = ? WHERE user_id = ?"""
                    data_tuple = (new_wallet, new_bank, member.id)
                else:
                    return False

            await self.bot.db.execute(sql, data_tuple)
            await self.bot.db.commit()
            return True

    async def gift(self, member, to, amount):
        pass

    async def get_inventory(self, member):
        sql = """SELECT inventory FROM economy WHERE user_id = ?"""
        data = (member.id,)

        cursor = await self.bot.db.execute(sql, data)
        data = await cursor.fetchone()

        return data[0]

    @commands.command(
        brief = "Deposita tus quacks al banco",
        usage = f"{config.prefix}depositar [cantidad]"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def depositar(self, ctx, amount):
        result = await self.transaction(ctx.author, amount, "to_bank")
        print(result)
        embed = discord.Embed(
            color = constants.blue
        )

        if result is True:
            amount = int(amount)
            embed.description = f"{constants.check} Has depositado {amount:,} quacks a tu banco"
            await ctx.send(embed = embed)

        if result == 3:
            embed.color = constants.red
            embed.description = f"{constants.x} Asegurate de ingresar un monto correcto."
            await ctx.send(embed = embed)

        if result is False:
            embed.color = constants.red
            embed.description = f"{constants.x} No tienes suficiente dinero para realizar esa transaccion.\nUsa el comando `balance` para ver tus quacks."
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Retira algunos quacks de tu banco",
        usage = f"{config.prefix}retirar [cantidad]"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def retirar(self, ctx, amount):
        result = await self.transaction(ctx.author, amount, "to_wallet")
        embed = discord.Embed(
            color = constants.blue
        )

        if result is True:
            amount = int(amount)
            embed.description = f"{constants.check} Has retirado {amount:,} quacks de tu banco"
            await ctx.send(embed = embed)

        if result == 3:
            embed.color = constants.red
            embed.description = f"{constants.x} Asegurate de ingresar un monto correcto."
            await ctx.send(embed = embed)

        if result is False:
            embed.color = constants.red
            embed.description = f"{constants.x} No tienes suficiente dinero para realizar esa transaccion.\nUsa el comando `balance` para ver tus quacks."
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra el balance del usario",
        usage = f"{config.prefix}balance [usario]"
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def balance(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        data = await self.get_balance(member)

        embed = discord.Embed(
            description = f"**Billetera:** {data[0]:,} quacks\n**Banco:** {data[1]:,} quacks \n**Total:** {data[0] + data[1]:,} quacks",
            color = constants.blue
        )
        embed.set_author(name = str(ctx.author), icon_url = ctx.author.avatar_url)

        await ctx.send(embed = embed)

    @commands.command(
        brief = "Pidele algunos quacks a alguien",
        usage = f"{config.prefix}pedir"
    )
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def pedir(self, ctx):
        rand_amount = random.randint(22, 70)
        chance = random.choices([rand_amount, 0], weights = [.7, .3])

        embed = discord.Embed(
            color = constants.blue
        )

        if chance[0] == rand_amount:
            await self.update_amount(ctx.author, rand_amount, "add")
            embed.description = random.choice(econstants.BEG_RESPONSE).replace("VAR", str(rand_amount))
            await ctx.send(embed = embed)

        if chance[0] == 0:
            embed.description = random.choice(econstants.BEG_NO_RESPONSE)
            embed.color = constants.red
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Busca en la basura, puede dar quacks, nada un item o una baja probabilidad de un pato dorado",
        usage = f"{config.prefix}buscar"
    )
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def buscar(self, ctx):
        rand_amount = random.randint(50, 100)
        chance = random.choices([rand_amount, 0, 1], weights = [.7, .3, .01])

        embed = discord.Embed(
            color = constants.blue
        )

        if chance[0] == 0:
            embed.description = random.choice(econstants.NOTHING_RESPONSE)
            embed.color = constants.red
            await ctx.send(embed = embed)
        if chance[0] == 1:
            await self.update_amount(ctx.author, 5000, "add")
            embed.description = "Encontraste un pato dorado y lo vendiste por **5,000** quacks"
            await ctx.send(embed = embed)
        if chance[0] == rand_amount:
            await self.update_amount(ctx.author, rand_amount, "add")
            embed.description = random.choice(econstants.FOUND_RESPONSE).replace("VAR", str(rand_amount))
            await ctx.send(embed = embed)

    @commands.command(
        brief = "Muestra todos los items que tiene el usuario.",
        usage = f"{config.prefix}inventario"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def inventario(self, ctx, member: discord.Member = None):
        print(await self.get_inventory(ctx.author))

    @commands.command(
        brief = "Muestra la tienda actual, cambia cada 4 horas",
        usage = f"{config.prefix}tienda"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def tienda(self, ctx, specific = None):

        if specific is not None:

            shop = ""
            embed = discord.Embed(
                color = constants.blue
            )
            for item in self.shop:
                shop = shop + f"{item['emoji']} **{item['name']}** ► [{item['price']:,} quacks](https://www.youtube.com/watch?v=RhT2M35tQlc) \n{item['description']}\n\n"

            embed.description = shop
            return await ctx.send(embed = embed)

        for item in self.shop:
            if item["name"].lower() == specific.lower():
                embed = discord.Embed(
                    title = item["name"],
                    description = f"{item["description"]}\n\n**Precio:** {item["price"]}",
                    color = constants.blue
                )
                embed.set_footer(text = "Puedes usar el comando `comprar` si te interesa.")
                file = discord.File(f"emotes/{item["file_code"]}.png", filename="image.png")
                embed.set_thumbnail(url="attachment://image.png")
                await ctx.send(file=file, embed=embed)


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
            data_tuple = (member.id, 0, 0, "[]", 0, None, None, None)

            await self.bot.db.execute(query, data_tuple)
            await self.bot.db.commit()

    @commands.command(hidden = True)
    @commands.is_owner()
    async def insert_economic(self, ctx):
        for member in ctx.guild.members:
            await self.if_not_insert(member)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id == 252962157002489857:
                await ctx.reinvoke()
                return
            await ctx.send(f"Mas lento, intenta de nuevo dentro de {error.retry_after:.2f} segundos")

        else:
            raise error


def setup(bot):
    bot.add_cog(Economia(bot))
