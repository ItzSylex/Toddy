import discord
import constants

from babel.dates import format_date


class CustomEmbed:

    def __init__(self, **kwargs):
        self.types = kwargs["types"]
        self.target = kwargs["target"]
        self.timestamp = kwargs["timestamp"]

    def create_embed(self):
        embed = discord.Embed()
        embed.color = constants.green

        if self.types == "ban":
            if self.is_obj() is False:
                embed.description = f"{constants.check} {self.target.display_name} ha sido **baneado**. {constants.ban}"
                return embed
            else:
                embed.description = f"{constants.check} {self.target.id} ha sido **baneado**. {constants.ban}"
                return embed

        if self.types == "mute":
            embed.description = f"{constants.check} {self.target.display_name} ha sido **silenciado**. {constants.mute}"
            return embed

        if self.types == "kick":
            embed.description = f"{constants.check} {self.target.display_name} ha sido **expulsado**. {constants.kick}"
            return embed

        if self.types == "unmute":
            if self.is_obj() is False:
                embed.description = f"{constants.check} {self.target.display_name} ya no esta **silenciado**. {constants.unmute}"
                return embed
            else:
                embed.description = f"{constants.check} {self.target.id} ya no esta **silenciado**. {constants.unmute}"
                return embed

        if self.types == "warn":
            embed.description = f"{constants.check} {self.target.display_name} ha recibido un **warn**. {constants.rwarn}"
            return embed

        if self.types == "error":
            embed.color = constants.red
            embed.description = f"{constants.alert} No puedes realizar esta accion con este usario."
            return embed

    def is_obj(self):
        if isinstance(self.target, discord.Object):
            return True
        return False
