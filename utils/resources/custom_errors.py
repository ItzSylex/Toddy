from discord.ext import commands


class NoRequiredRole(commands.DisabledCommand):
    def __init__(self):
        super().__init__("No tienes los roles necesarios para usar este comando")