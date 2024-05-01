import json

import disnake
from disnake.ext import commands
from mysql.connector import (connection)

db = connection.MySQLConnection(user="Marai",
                                password="MARAIFS*34754SFDG_$7^FSGJnfsdg#@#$$",
                                host="192.168.8.16",
                                database="DiscordBots")
cursor = db.cursor()


class CommandsLevel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = self.load_levels()
        self.guild_id = 847415392485376050

    @commands.slash_command(name="level", guild_ids=[847415392485376050])
    async def level(self, ctx):
        pass

    # @level.sub_command(name="add", description="Добавить уровень игроку")

    def load_levels(self):
        with open('./cogs/utils.json', 'r') as file:
            return json.load(file)

    def check_level(self, user_id, exp, level):
        required_exp = self.levels["Levels"].get(str(level), None)
        if int(required_exp) is not None and exp >= int(required_exp):
            return level + 1
        return level

    def add_exp(self, user_id, exp):
        cursor.execute(f"SELECT exp, level FROM Level WHERE user_id = {user_id}")
        result = cursor.fetchone()

        if result is None:
            cursor.execute(f"INSERT INTO Level (user_id, exp, level) VALUES ({user_id}, {exp}, 1)")
        else:
            current_exp, level = result
            new_exp = current_exp + exp
            new_level = self.check_level(user_id, new_exp, level)
            cursor.execute(f"UPDATE Level SET exp = {new_exp}, level = {new_level} WHERE user_id = {user_id}")

        db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()
        if message.author.bot:
            return
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            self.add_exp(message.author.id, 1)
        else:
            print("Сервер не найден")


def setup(bot):
    bot.add_cog(CommandsLevel(bot))
