import asyncio
import random
from datetime import datetime, timezone, timedelta

import disnake
from disnake.ext import commands
from disnake.ui import Button
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
        self.button = Buttons()

        self.id_guild = 847415392485376050
        self.dep = 0

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
                        description=f"Вы успешно создали роль {role.mention}\n\n{currency} **Баланс:**\n```{check_balance[0][0]}```",
                        member=interaction)
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

    # @role.sub_command(name="inventory", description="Просмотр инвенторя ролей пользователя",
    #                   guild_ids=[847415392485376050])
    # async def role_inventory(self, interaction: disnake.AppCommandInteraction,
    #                          member: disnake.Member = commands.Param(name="участник",
    #                                                                  description="Выберите пользователя для взаимодействия",
    #                                                                  default=False)):
    #     await interaction.response.defer(ephemeral=True)
    #     check_roles_author = self.query.qselect("role_id", "Inventory", f"user_id = {interaction.author.id}")
    #     check_roles_member = self.query.qselect("role_id", "Inventory", f"user_id = {interaction.author.id}")
    #     if member:
    #         if check_roles_member[0][0]:
    #             emb = self.embeds.inventory(member=member, name=f"{check_roles_member[0][0]}")
    #             await interaction.send(embed=emb, ephemeral=True)
    #         else:
    #             emb = self.embeds.inventory(member=member, name="Этот инвентарь **пустует** на данный момент")
    #             await interaction.send(embed=emb, ephemeral=True)
    #     else:
    #         if check_roles_author[0][0]:
    #             pass
    #         else:
    #             emb = self.embeds.inventory(member=member, name="Этот инвентарь **пустует** на данный момент")
    #             await interaction.send(embed=emb, ephemeral=True)

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
                                   value1=f"`user_id`, `user_balance`, `user_bank`",
                                   value2=f"'{member.id}','0', '0'")
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
                                   value1=f"`user_id`, `user_balance`, `user_bank`",
                                   value2=f"'{interaction.author.id}','0', '0'")
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
                    emb = self.embeds.success(description=f"Вы успешно добавили **<@{member.id}>** {count} {currency}",
                                              member=interaction)
                    await interaction.send(embed=emb, ephemeral=True)
                else:
                    self.query.qinsert(what="`Economy`",
                                       value1=f"`user_id`, `user_balance`, `user_bank`",
                                       value2=f"'{member.id}','{count}', '0'")
                    emb = self.embeds.info(title="Успешное создание записи",
                                           description=f"Вы успешно создали запись с именем\n```{member.display_name}```",
                                           member=member)
                    semb = self.embeds.success(description=f"Вы успешно добавили **<@{member.id}>** {count} {currency}",
                                               member=interaction)
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
                    embed = self.embeds.success(description=f"Вы успешно добавили **себе** {count} {currency}",
                                                member=interaction)
                    await interaction.send(embed=embed, ephemeral=True)
                else:
                    self.query.qinsert(what="`Economy`",
                                       value1=f"`user_id`, `user_balance`, `user_bank`",
                                       value2=f"'{interaction.author.id}','{count}', '0'")
                    emb = self.embeds.info(title="Успешное создание записи",
                                           description=f"Вы успешно создали запись с именем\n```{interaction.author.display_name}```",
                                           member=interaction.author)
                    semb = self.embeds.success(description=f"Вы успешно добавили **себе** {count} {currency}",
                                               member=interaction)
                    await interaction.send(embed=emb, ephemeral=True)
                    await interaction.send(embed=semb, ephemeral=True)
            else:
                embed = self.embeds.error(description="**У вас недостаточно прав!**")
                await interaction.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="pay", description="Передать деньги игроку", guild_ids=[847415392485376050])
    async def pay(self,
                  interaction,
                  member: disnake.Member = commands.Param(name="участник",
                                                          description="Выбор участника"),
                  count=commands.Param(name="количество",
                                       description="Сколько передать")):
        await interaction.response.defer(ephemeral=True)
        check_author_balance = self.query.qselect(what="user_balance",
                                                  where="Economy",
                                                  condition=f"user_id = {interaction.author.id}")
        check_member_balance = self.query.qselect(what="user_balance",
                                                  where="Economy",
                                                  condition=f"user_id = {member.id}")

        print(check_member_balance, check_author_balance)
        if int(count) > int(check_author_balance[0][0]):
            embed = self.embeds.error(description="В вашем кошельке кажется **не хватает** денег!")
            await interaction.send(embed=embed)
        else:
            if check_member_balance[0][0]:
                self.query.qupdate(what="`Economy`",
                                   where=f"`user_id` = '{interaction.author.id}'",
                                   set=f"`user_balance` = `user_balance` - '{count}'")
                self.query.qupdate(what="`Economy`",
                                   where=f"`user_id` = '{member.id}'",
                                   set=f"`user_balance` = `user_balance` + '{count}'")
                cnx.commit()

                embed = self.embeds.success(
                    description=f"Вы успешно перевели\n **{count}** {currency} игроку {member.mention}",
                    member=interaction)
                await interaction.send(embed=embed)

            else:
                embed = self.embeds.error(
                    description="Пользователь не найден в базе данных!\nПопросите его прописать любую команду экономики")
                await interaction.send(embed=embed)

    @commands.slash_command(name="coinflip", description="Игра орёл или решка", guild_ids=[847415392485376050])
    async def coinflip(self, interaction,
                       count=commands.Param(name="количество", description="Сколько поставить ставку",
                                            min_length=3, max_length=5)):
        await interaction.response.defer()
        check_member_balance = self.query.qselect(what="user_balance", where="Economy",
                                                  condition=f"`user_id` = '{interaction.author.id}'")
        if int(count) > int(check_member_balance[0][0]):
            embed = self.embeds.error(description="Кажется в вашем кошельке **недосататочно** денег!")
            await interaction.send(embed=embed)
        else:
            buttons = self.button.coinflip()

            embed = self.embeds.info(title=f"{interaction.author.display_name} — Монетка",
                                     description="Выберите сторону, нажав на кнопки ниже!",
                                     member=interaction.author)
            self.dep = int(count)
            await interaction.send(embed=embed, components=[buttons])

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id in ["btn1", "btn2"]:
            count = self.dep

            choice = "Орёл" if inter.component.custom_id == "btn1" else "Решка"
            gif = "https://usagif.com/wp-content/uploads/gifs/coin-flip-13.gif"
            embed = disnake.Embed(colour=0x36393F)
            embed.set_image(url=gif)
            await inter.message.edit(embed=embed)
            await asyncio.sleep(1)
            if random.choice(['орёл', 'решка']) == choice.lower():
                print("win")
                win_amount = count + (0.2 * count)
                embed.description = f"Выпал орёл, ваша награда составила {win_amount}{currency}"
                embed.set_image(url=None)
                await inter.message.edit(embed=embed, components=[])
                # self.query.qupdate(what="`Economy`",
                #                    where=f"`user_id` = '{interaction.author.id}'",
                #                    set=f"`user_balance` = `user_balance` + '{win_amount}'")
            else:
                print("lose")
                lose_amount = count - (0.2 * count)
                embed.description = f"Выпал орёл, ваш проигрыш составил {lose_amount}{currency}"
                embed.set_image(url=None)
                await inter.message.edit(embed=embed, components=[])
        elif inter.component.custom_id == "close":
            await inter.message.delete()

    @commands.slash_command(name="bank", guild_ids=[847415392485376050])
    async def bank(self, interaction):
        pass

    @commands.is_owner()
    @commands.slash_command(name='empty', default_member_permissions=1, guild_ids=[387409949442965506])
    async def empty(self, ctx):
        for member in ctx.guild.members:
            if len(member.roles) == 1:
                guild = self.bot.get_guild(387409949442965506)
                role = guild.get_role(1029037374434463815)
                channel = self.bot.get_channel(1108094157978865745)  # 1119634958852558938,
                await member.add_roles(role)
                await channel.send(f"{role} -> {member.mention}")

    @bank.sub_command(name="info", description="Узнать счёт в банке", guild_ids=[847415392485376050])
    async def bank_info(self, interaction):
        await interaction.response.defer(ephemeral=True)
        bank = self.query.qselect(what="*", where="Economy", condition=f"`user_id` = '{interaction.author.id}'")

        if bank:
            count = cursor.execute(f"""SELECT user_bank FROM `Economy` WHERE `user_id` = '{interaction.author.id}'""")
            count = cursor.fetchone()
            embed = self.embeds.bank(member=interaction, count=count[0])
            await interaction.send(embed=embed)
        else:
            self.query.qinsert(what="`Economy`",
                               value1=f"`user_id`, `user_balance`, `user_bank`",
                               value2=f"'{interaction.author.id}','0', '0'")
            emb = self.embeds.info(title="Успешное создание записи",
                                   description=f"Вы успешно создали счёт в банке!",
                                   member=interaction.author)
            await interaction.send(embed=emb, ephemeral=True)
            embed = self.embeds.bank(member=interaction, count="0")
            await interaction.send(embed=embed)

    @bank.sub_command(name="pay", description="Перевести деньги игроку из банка")
    async def bank_pay(self, interaction,
                       member: disnake.Member = commands.Param(name="участник",
                                                               description="Выбор участника"),
                       count=commands.Param(name="количество",
                                            description="Сколько передать")):
        check_bank_balance = self.query.qselect(what="user_balance", where="Economy",
                                                condition=f"`user_id` = '{interaction.author.id}'")
        check_member_balance = self.query.qselect(what="*", where="Economy", condition=f"`user_id` = '{member.id}'")
        if int(check_bank_balance[0][0]) < int(count):
            embed = self.embeds.error(description="В банке недостаточно средств!")
            await interaction.send(embed=embed, ephemeral=True)
        else:
            if member:
                if check_member_balance[0][0]:
                    self.query.qupdate(what="`Economy`",
                                       where=f"`user_id` = '{interaction.author.id}'",
                                       set=f"`user_bank` = `user_bank` - '{count}'")
                    self.query.qupdate(what="`Economy`",
                                       where=f"`user_id` = '{member.id}'",
                                       set=f"`user_balance` = `user_balance` + '{count}'")
                    cnx.commit()

                    embed = self.embeds.success(
                        description=f"Вы успешно перевели\n **{count}** {currency} с **банковского счёта**\nигроку {member.mention}",
                        member=interaction)
                    await interaction.send(embed=embed)
                else:
                    embed = self.embeds.error(description="У пользователя нет счёта!")
                    await interaction.send(embed=embed, ephemeral=True)
            else:
                embed = self.embeds.error(description="Указанный игрок не найден!")
                await interaction.send(embed=embed, ephemeral=True)

    @bank.sub_command(name="deposit", description="Внести деньги в банк")
    async def deposit(self, interaction, count=commands.Param(name="количество", description="Сколько внести")):
        check_balance_bank = self.query.qselect(what="*", where="Economy",
                                                condition=f"`user_id` = '{interaction.author.id}'")
        check_member_balance = self.query.qselect(what="user_balance", where="Economy",
                                                  condition=f"`user_id` = '{interaction.author.id}'")

        if check_balance_bank:
            if int(check_member_balance[0][0]) < int(count):
                embed = self.embeds.error(description="В вашем кошельке кажется **не хватает** денег!")
                await interaction.send(embed=embed)
            else:
                self.query.qupdate(what="`Economy`",
                                   where=f"`user_id` = '{interaction.author.id}'",
                                   set=f"`user_balance` = `user_balance` - '{count}'")
                self.query.qupdate(what="`Economy`",
                                   where=f"`user_id` = '{interaction.author.id}'",
                                   set=f"`user_bank` = `user_bank` + '{count}'")
                cnx.commit()

                embed = self.embeds.success(
                    description=f"Вы успешно пополнили счёт в банке на {currency}\n```{count}```",
                    member=interaction)
                await interaction.send(embed=embed)
        else:
            try:
                self.query.qinsert(what="`Economy`",
                                   value1=f"`user_id`, `user_balance`, `user_bank`",
                                   value2=f"'{interaction.author.id}','0', '0'")
                embed = self.embeds.info(title="Успешное создание банковского счёта",
                                         description=f"Вы успешно создали банковский счёт\n```Пожалуйста, повторите команду!```",
                                         member=interaction.author)
                await interaction.send(embed=embed, ephemeral=True)
            except BaseException:
                pass

    @bank.sub_command(name="withdraw", description="Снять деньги с банка")
    async def withdraw(self, interaction, count=commands.Param(name="количество", description="Сколько снять")):
        check_balance_bank = self.query.qselect(what="*", where="Economy",
                                                condition=f"`user_id` = '{interaction.author.id}'")

        if int(count) > int(check_balance_bank[0][0]):
            embed = self.embeds.error(description="У вас в банке недостаточно средств!")
            await interaction.send(embed=embed)
        else:
            try:
                self.query.qupdate(what="`Economy`",
                                   where=f"`user_id` = '{interaction.author.id}'",
                                   set=f"`user_balance` = `user_balance` + '{count}'")
                self.query.qupdate(what="`Economy`",
                                   where=f"`user_id` = '{interaction.author.id}'",
                                   set=f"`user_bank` = `user_bank` - '{count}'")
                cnx.commit()

                embed = self.embeds.success(
                    description=f"Вы успешно сняли с банковского счёта {currency}\n```{count}```", member=interaction)
                await interaction.send(embed=embed)
            except BaseException:
                embed = self.embeds.error(description="Что-то пошло не так.. Сообщите администрации")
                await interaction.send(embed=embed)


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

    def bank(self, member, count):
        embed = disnake.Embed(title=f"", description=f"**Банковский счёт** - {member.author.mention}",
                              colour=self.color)
        embed.add_field(name=f"", value=f"В вашем банке сейчас:\n```{count}```")
        try:
            embed.set_thumbnail(url=member.author.avatar.url)
        except BaseException:
            pass
        return embed

    def success(self, description, member):
        embed = disnake.Embed(title=f"<a:Yes_Check:877264845504917565> Успешно",
                              description=f"{description}",
                              colour=self.color)
        try:
            embed.set_thumbnail(url=member.author.avatar.url)
        except BaseException:
            pass
        return embed

    def info(self, title, description, member):
        embed = disnake.Embed(title=f"{title}",
                              description=f"{description}",
                              colour=self.color)
        try:
            embed.set_thumbnail(url=member.avatar.url)
        except BaseException as eb:
            pass
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


class Buttons:

    def coinflip(self):
        button = [
            Button(style=disnake.ButtonStyle.grey,
                   custom_id="btn1",
                   label="Орёл"),
            Button(style=disnake.ButtonStyle.grey,
                   custom_id="btn2",
                   label="Решка"),
            Button(style=disnake.ButtonStyle.grey,
                   custom_id="close",
                   label="Завершить игру")
        ]
        return button


def setup(bot):
    bot.add_cog(Commands(bot))
