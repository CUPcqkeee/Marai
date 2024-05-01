import json
from datetime import datetime

import disnake
import mysql.connector
from disnake.ext import commands
from main import cnx as db

cursor = db.cursor()
voice_time_trackers = {}


class VoiceTimeTracker(commands.Cog):
    def __init__(self, member_id, bot):
        self.bot = bot
        self.member_id = member_id
        self.start_time = None
        self.levels = self.load_levels()

    def start_tracking(self):
        self.start_time = datetime.utcnow()

    def stop_tracking(self):
        if self.start_time:
            end_time = datetime.utcnow()
            duration = end_time - self.start_time
            self.add_exp(user_id=self.member_id, exp=1)
            self.save_to_database(duration)
            self.start_time = None

    def save_to_database(self, duration):
        total_seconds = int(duration.total_seconds())
        cursor.execute(f"""SELECT * FROM `VoiceTracker` WHERE `user_id` = '{self.member_id}'""")
        check_user = cursor.fetchone()
        if check_user:
            try:
                cursor.execute(f"""UPDATE `VoiceTracker` SET `duration` = `duration` + '{total_seconds}' 
                WHERE `user_id` = {self.member_id}""")
                db.commit()
            except BaseException as e:
                print(f"Error: {e}")
        else:
            cursor.execute(
                f"""INSERT INTO `VoiceTracker`(`user_id`, `duration`) 
                VALUES ('{self.member_id}','{total_seconds}')""")
            db.commit()


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
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not member.guild.id == 847415392485376050:
            return

        if before.channel != after.channel:
            user_id = member.id

            if before.channel:
                if user_id in voice_time_trackers:
                    voice_time_trackers[user_id].stop_tracking()

            if after.channel:
                if user_id not in voice_time_trackers:
                    voice_time_trackers[user_id] = VoiceTimeTracker(user_id, bot=self.bot)
                voice_time_trackers[user_id].start_tracking()


def setup(bot):
    bot.add_cog(VoiceTimeTracker(bot=bot, member_id=None))
