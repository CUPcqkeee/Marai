import disnake
from disnake.ext import commands

from main import cnx as db

cursor = db.cursor()


class TrackMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id_channels = [1202589645603344404, 1203374646787833876]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.id_channels:
            self.update_database(message.author.id)

    def update_database(self, user_id):
        cursor.execute(f"SELECT * FROM `MessageTracker` WHERE `user_id` = '{user_id}'")
        existing_record = cursor.fetchone()
        if existing_record:
            cursor.execute(
                f"""UPDATE `MessageTracker` SET `count` = `count` + '1' WHERE `user_id` = '{user_id}'""")
        else:
            cursor.execute(f"""INSERT INTO `MessageTracker`(`user_id`, `count`) VALUES ('{user_id}','1')""")

        db.commit()


def setup(bot):
    bot.add_cog(TrackMessage(bot))
