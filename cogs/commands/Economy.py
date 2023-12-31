from datetime import datetime, timezone, timedelta

import disnake
from disnake.ext import commands
from mysql.connector import (connection)

cnx = connection.MySQLConnection(user="Marai",
                                 password="MARAIFS*34754SFDG_$7^FSGJnfsdg#@#$$",
                                 host="192.168.8.16",
                                 database="DiscordBots")
cursor = cnx.cursor()

currency = "<:panda_coin:1190791710343700500>"


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.query = Query()
        self.embeds = Embeds(bot)
        self.id_guild = 847415392485376050

    @commands.slash_command(guild_ids=[847415392485376050])
    async def role(self, interaction):
        pass

    @role.sub_command(name="create", description="Создать личную роль | Стоимость: 10000",
                      guild_ids=[847415392485376050])
    async def role_create(self,
                          interaction: disnake.AppCommandInteraction,
                          name=commands.Param(name="название", description="Укажите название роли"),
                          color=commands.Param(name="цвет", description="Укажите цвет роли в HEX формате")):
        await interaction.response.defer(ephemeral=True)
        guild = self.bot.get_guild(self.id_guild)
        check_balance = self.query.qselect(what="user_balance",
                                           where="Economy",
                                           condition=f"`user_id` = '{interaction.author.id}'")
        if check_balance[0][0] >= 10000:
            validate = True
            for role_name in guild.roles:
                if role_name.name == name:
                    validate = False
            if validate:
                scolor = disnake.Color(int(color, 16))
                if scolor:
                    self.query.qupdate(what="`Economy`",
                                       where=f"`user_id` = '{interaction.author.id}'",
                                       set=f"`user_balance` = `user_balance` - '10000'")
                    role = await guild.create_role(name=name, color=scolor)
                    self.query.qinsert(what="`Inventory`",
                                       value1=f"`user_id`, `role_id`",
                                       value2=f"'{interaction.author.id}','{role.id}'")
                    emb = self.embeds.success(
                        description=f"Вы успешно создали роль {role.mention}\n\n{currency} **Баланс:**\n```{check_balance[0][0]}```")
                    await interaction.send(embed=emb, ephemeral=True)
                    member = interaction.guild.get_member(interaction.author.id)
                    await member.add_roles(role, reason="Создание личной роли")
                else:
                    emb = self.embeds.error(description="Вы ввели неверный/не существующий цвет!")
                    await interaction.send(embed=emb, ephemeral=True)
            else:
                embed = self.embeds.error(description=f"Роль с названием **{name}** уже существует!")
                await interaction.send(embed=embed, ephemeral=True)

        else:
            emb = self.embeds.error(description="У вас недостаточно валюты!")
            await interaction.send(embed=emb, ephemeral=True)

    @role.sub_command(name="inventory", description="Просмотр инвенторя ролей пользователя",
                      guild_ids=[847415392485376050])
    async def role_inventory(self, interaction: disnake.AppCommandInteraction,
                             member: disnake.Member = commands.Param(name="участник",
                                                                     description="Выберите пользователя для взаимодействия",
                                                                     default=False)):
        await interaction.response.defer(ephemeral=True)
        check_roles_author = self.query.qselect("role_id", "Inventory", f"user_id = {interaction.author.id}")
        check_roles_member = self.query.qselect("role_id", "Inventory", f"user_id = {interaction.author.id}")
        if member:
            if check_roles_member[0][0]:
                emb = self.embeds.inventory(member=member, name=f"{check_roles_member[0][0]}")
                await interaction.send(embed=emb, ephemeral=True)
            else:
                emb = self.embeds.inventory(member=member, name="Этот инвентарь **пустует** на данный момент")
                await interaction.send(embed=emb, ephemeral=True)
        else:
            if check_roles_author[0][0]:
                pass
            else:
                emb = self.embeds.inventory(member=member, name="Этот инвентарь **пустует** на данный момент")
                await interaction.send(embed=emb, ephemeral=True)

    @commands.slash_command(name="balance", description="Узнать баланс", guild_ids=[847415392485376050])
    async def balance(self,
                      interaction: disnake.AppCommandInteraction,
                      member: disnake.Member = commands.Param(
                          name="участник",
                          description="Выбор участника",
                          default=None
                      )):
        await interaction.response.defer(ephemeral=True)
        check_author = self.query.qselect(what="user_balance",
                                          where="Economy",
                                          condition=f"user_id = {interaction.author.id}")
        if member:
            check_member = self.query.qselect(what="user_balance",
                                              where="Economy",
                                              condition=f"user_id = {member.id}")
            if check_member:
                try:
                    balance = self.query.qselect(what="user_balance",
                                                 where="Economy",
                                                 condition=f"user_id = {member.id}")
                    embed = self.embeds.info(title=f"Баланс - {member.display_name}",
                                             description=f"{currency} **Баланс:**\n```{balance[0][0]}```",
                                             member=member)
                    await interaction.send(embed=embed, ephemeral=True)
                except BaseException as event:
                    print(event)
                    errembed = self.embeds.error(
                        description=f"**Не нашла <@{member.id}> в базе данных**\n> Обратитесь к <@589492162211610662> за помощью")
                    await interaction.send(embed=errembed, ephemeral=True)
            else:
                self.query.qinsert(what="`Economy`",
                                   value1=f"`user_id`, `user_balance`",
                                   value2=f"'{member.id}','0'")
                emb = self.embeds.info(title="Успешное создание записи",
                                       description=f"Вы успешно создали запись с именем\n```{member.display_name}```",
                                       member=member)
                semb = self.embeds.info(title=f"Баланс - {member.display_name}",
                                        description=f"{currency} **Баланс:**\n```0```",
                                        member=member)
                await interaction.send(embed=emb, ephemeral=True)
                await interaction.send(embed=semb, ephemeral=True)
        else:
            if check_author:
                try:
                    balance = self.query.qselect(what="user_balance",
                                                 where="Economy",
                                                 condition=f"user_id = {interaction.author.id}")
                    embed = self.embeds.info(title=f"Баланс - {interaction.author.display_name}",
                                             description=f"{currency} **Баланс:**\n```{balance[0][0]}```",
                                             member=interaction.author)
                    await interaction.send(embed=embed, ephemeral=True)
                except BaseException as event:
                    print(event)
                    errembed = self.embeds.error(
                        description="**Не нашла Вас в базе данных**\nОбратитесь к <@589492162211610662>")
                    await interaction.send(embed=errembed, ephemeral=True)
            else:
                self.query.qinsert(what="`Economy`",
                                   value1=f"`user_id`, `user_balance`",
                                   value2=f"'{interaction.author.id}','0'")
                emb = self.embeds.info(title="Успешное создание записи",
                                       description=f"Вы успешно создали запись с именем\n```{interaction.author.display_name}```",
                                       member=interaction.author)
                semb = self.embeds.info(title=f"Баланс - {interaction.author.display_name}",
                                        description=f"{currency} **Баланс:**\n```0```",
                                        member=interaction.author)
                await interaction.send(embed=emb, ephemeral=True)
                await interaction.send(embed=semb, ephemeral=True)

    @commands.slash_command(name="award", description="Выдать пандакоинов", guild_ids=[847415392485376050])
    async def award(self,
                    interaction,
                    member: disnake.Member = commands.Param(name="участник",
                                                            description="Выбор участника",
                                                            default=None
                                                            ),
                    count=commands.Param(name="количество",
                                         description="Сколько добавить")):
        perms = self.query.qselect(what="lvlrights",
                                   where="Perms",
                                   condition=f"user_id = {interaction.author.id}")
        check_author = self.query.qselect(what="user_balance",
                                          where="Economy",
                                          condition=f"user_id = {interaction.author.id}")
        if member:
            check_member = self.query.qselect(what="user_balance",
                                              where="Economy",
                                              condition=f"user_id = {member.id}")
            if perms[0][0] == "ADM" or perms[0][0] == "OWN":
                if check_member:
                    self.query.qupdate(what="`Economy`",
                                       where=f"`user_id` = '{member.id}'",
                                       set=f"`user_balance` = `user_balance` + '{count}'")
                    emb = self.embeds.success(description=f"Вы успешно добавили **<@{member.id}>** {count} {currency}")
                    await interaction.send(embed=emb, ephemeral=True)
                else:
                    self.query.qinsert(what="`Economy`",
                                       value1=f"`user_id`, `user_balance`",
                                       value2=f"'{member.id}','{count}'")
                    emb = self.embeds.info(title="Успешное создание записи",
                                           description=f"Вы успешно создали запись с именем\n```{member.display_name}```",
                                           member=member)
                    semb = self.embeds.success(description=f"Вы успешно добавили **<@{member.id}>** {count} {currency}")
                    await interaction.send(embed=emb, ephemeral=True)
                    await interaction.send(embed=semb, ephemeral=True)
            else:
                embed = self.embeds.error(description="**У вас недостаточно прав!**")
                await interaction.send(embed=embed, ephemeral=True)
        else:
            if perms[0][0] == "ADM" or perms[0][0] == "OWN":
                # print(check_author)
                if check_author:
                    self.query.qupdate(what="`Economy`",
                                       where=f"`user_id` = '{interaction.author.id}'",
                                       set=f"`user_balance` = `user_balance` + '{count}'")
                    embed = self.embeds.success(description=f"Вы успешно добавили **себе** {count} {currency}")
                    await interaction.send(embed=embed, ephemeral=True)
                else:
                    self.query.qinsert(what="`Economy`",
                                       value1=f"`user_id`, `user_balance`",
                                       value2=f"'{interaction.author.id}','{count}'")
                    emb = self.embeds.info(title="Успешное создание записи",
                                           description=f"Вы успешно создали запись с именем\n```{interaction.author.display_name}```",
                                           member=interaction.author)
                    semb = self.embeds.success(description=f"Вы успешно добавили **себе** {count} {currency}")
                    await interaction.send(embed=emb, ephemeral=True)
                    await interaction.send(embed=semb, ephemeral=True)
            else:
                embed = self.embeds.error(description="**У вас недостаточно прав!**")
                await interaction.send(embed=embed, ephemeral=True)


class Embeds:
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x36393F
        self.time = datetime.now(timezone(timedelta(hours=+3)))
        self.d_time = self.time.strftime('%H:%M')

    def error(self, description):
        embed = disnake.Embed(title=f"<a:No_Check:877264845366517770> Произошла ошибка",
                              description=f"{description}",
                              colour=self.color)
        return embed

    def success(self, description):
        embed = disnake.Embed(title=f"<a:Yes_Check:877264845504917565> Успешно",
                              description=f"{description}",
                              colour=self.color)
        return embed

    def info(self, title, description, member):
        embed = disnake.Embed(title=f"{title}",
                              description=f"{description}",
                              colour=self.color)
        embed.set_thumbnail(url=member.avatar.url)
        return embed

    def inventory(self, name, member):
        embed = disnake.Embed(colour=self.color)
        embed.set_author(name=f"{member.display_name} — Инвентарь ролей пользователя", icon_url=member.avatar.url)
        embed.add_field(name=f"", value=f"{name}")
        return embed


class Query:

    def qselect(self, what, where, condition=None):
        if condition:
            cursor.execute(f"""SELECT {what} FROM {where} WHERE {condition}""")
        else:
            cursor.execute(f"""SELECT {what} FROM {where}""")

        result = cursor.fetchall()
        return result

    def qinsert(self, what, value1, value2):
        cursor.execute(f"""INSERT INTO {what} ({value1}) VALUES ({value2})""")
        cnx.commit()

    # UPDATE `Economy` SET `user_id`='[value-1]',`user_balance`='[value-2]' WHERE 1
    def qupdate(self, what, set, where):
        cursor.execute(f"""UPDATE {what} SET {set} WHERE {where}""")
        cnx.commit()


def setup(bot):
    bot.add_cog(Commands(bot))
