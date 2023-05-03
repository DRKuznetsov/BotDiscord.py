import re
import pandas as pd
import discord
import asyncio
import datetime as dt
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput

# test
# bi_rpa_guild = 1102922511257186305
# su_report = 1102922512028930068
# su_send = 1102922512028930070
# prod
bi_rpa_guild = 1088107116042129548
su_report = 1088350602150543380
su_send = 1088447246560935986


class StandUpModal(Modal, title="Стендап"):
    su_com = TextInput(
        style=discord.TextStyle.short,
        label="Есть ли коммерческие задачи на сегодня?",
        placeholder="Да/Нет",
        max_length=16,
        required=True
    )
    su_content = TextInput(
        style=discord.TextStyle.long,
        label="Что вы собираетесь делать?",
        placeholder="Разработка. 8 часов.",
        max_length=1024,
        required=True
    )
    su_pm = TextInput(
        style=discord.TextStyle.short,
        label="Кто ваш руководитель по задачам?",
        placeholder="ФИ руководителя",
        max_length=128,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        print("Обработка Стендапа От " + interaction.user.name)
        channel = client.get_channel(su_report)
        usercolor = await client.fetch_user(interaction.user.id)
        embed = discord.Embed(title="Стендап", color=usercolor.accent_color)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        try:
            avatar = interaction.user.avatar.url
            embed.set_author(name=interaction.user, icon_url=avatar)
        except:
            avatar = interaction.user.default_avatar.url
            embed.set_author(name=interaction.user, icon_url=avatar)
        embed.add_field(name="Коммерческая задача:", value=str(self.su_com), inline=True)
        embed.add_field(name="Руководитель по задачам:", value=str(self.su_pm), inline=True)
        embed.add_field(name="План на сегодня:", value=str(self.su_content), inline=False)
        await channel.send(embed=embed)
        try:
            await interaction.response.send_message()
        except:
            print("Стендап Обработан От " + interaction.user.name)

        myguild = client.get_guild(bi_rpa_guild)
        allroles = myguild.roles

        try:
            idx_role = next(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(allroles)))[0]
            myrole = allroles[idx_role]
            iduser = interaction.user.id
            user = myguild.get_member(int(iduser))
            await user.add_roles(myrole)
            await user.send(embed=embed)
        except:
            print("Can Not Assign Role")

    async def on_error(self, interaction: discord.Interaction, error):
        print(error)


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Выступить', style=discord.ButtonStyle.blurple, custom_id='persistent_view:blurple')
    async def blurple(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StandUpModal())


class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(PersistentView())

    async def on_ready(self):
        standup.start()
        standup_end.start()
        ksyp.start()
        notify.start()
        notify_last.start()
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('-----')


client = PersistentViewBot()


@tasks.loop(hours=24)
async def standup_end():
    limit = 0
    my_channel = client.get_channel(su_send)
    async for _ in my_channel.history(limit=None):
        limit += 1
    await my_channel.purge(limit=limit)


@standup_end.before_loop
async def before_standup_end():
    for _ in range(60 * 60 * 24):
        if dt.datetime.now().strftime("%H:%M") == "12:00" and dt.datetime.now().weekday() < 5:
            print('It is time for standup to end')
            return
        await asyncio.sleep(31)


@tasks.loop(hours=24)
async def ksyp():
    dataNew = pd.read_excel(
        "C:\\Users\\dlmorozenko\\Documents\\PIX\\SlackDOsendData\\Незаполненные ежедневные отчеты (XLSX).xlsx")

    dataNew = dataNew.dropna(axis=1, how='all')
    dataNew.columns = [1, 2, 3, 4, 5]
    dataNew = dataNew.drop(columns=[2, 4, 5])
    dataNew = dataNew[dataNew[1].str.contains("Спортивная") == False].reset_index(drop=True)
    dataNew = dataNew.drop([0, 1, 2, 3]).reset_index(drop=True)

    del_indexes = []

    for ind, row in enumerate(dataNew.values):
        if row[0] == "БОТ BI и RPA":
            del_indexes.append(ind)
            continue
        if len(del_indexes) > 0:
            if len(re.findall("[А-ЯЁ][а-яё]+", row[0])) == 0:
                del_indexes.append(ind)
            else:
                break

    dataNew = dataNew.drop(index=del_indexes)
    dataNew = dataNew.fillna("")
    stringdflong = dataNew.to_string(header=False, index=False)
    names = re.findall("[А-ЯЁ][а-яё]+ *[А-ЯЁ][а-яё]+(?= *[А-ЯЁ][а-яё]+)", stringdflong)
    list_users = client.users
    tagline = ''
    non_tagline = ''
    for name in names:
        try:
            new_name = re.findall("\w*", name)[2] + ' ' + re.findall("\w*", name)[0]
            id = next(filter(lambda x: x[1].name == new_name, enumerate(list_users)))[0]
            tagline = tagline + '<@!' + str(list_users[id].id) + '> '
        except:
            non_tagline = non_tagline + re.findall("\w*", name)[2] + ' ' + re.findall("\w*", name)[0] + '; '

    channel = client.get_channel(1101469177484677180)

    await channel.send(content='Око КСУП следит за вами')
    await channel.send(stringdflong[0:2000])
    lgth = len(stringdflong)
    counter = 2000
    while (counter < lgth):
        stringdf = stringdflong[counter:counter + 2000]
        await channel.send(content=stringdf)
        counter += 2000
    await channel.send(content=tagline)
    if non_tagline != '':
        await channel.send(content="Я не смог вас отметить, но знайте я все вижу: " + non_tagline)


@ksyp.before_loop
async def before_ksyp():
    for _ in range(60 * 60 * 24):
        if dt.datetime.now().strftime("%H:%M") == "14:10" and dt.datetime.now().weekday() < 5:
            print('It is time for ksyp')
            return
        await asyncio.sleep(31)


@tasks.loop(hours=24)
async def standup():
    myguild = client.get_guild(bi_rpa_guild)
    allroles = myguild.roles
    try:
        idx_role = next(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(allroles)))[0]
        myrole = allroles[idx_role]
        await myrole.delete()
    except:
        print("Role Not Found")
    await myguild.create_role(name="Золотой Человек", color=discord.Colour.gold())

    text = "@everyone Время для утреннего стендапа!"

    channel = client.get_channel(su_send)
    await channel.send(text, view=PersistentView())
    su_channel = client.get_channel(su_report)
    await su_channel.send(content='<@&1088108846775554128> Новый день - Новый стендап!')


@standup.before_loop
async def before_standup():
    for _ in range(60 * 60 * 24):
        if dt.datetime.now().strftime("%H:%M") == "09:00" and dt.datetime.now().weekday() < 5:
            print('It is time for standup')
            return
        await asyncio.sleep(31)


@tasks.loop(hours=24)
async def notify():
    try:
        myguild = client.get_guild(bi_rpa_guild)
        list_users = myguild.members

        for user in list_users:
            user_roles = user.roles
            if any(filter(lambda x: x[1].name == 'Производство', enumerate(user_roles))):
                if any(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(user_roles))):
                    print(user.name + " published standup")
                else:
                    print(user.name + " need a reminder")
                    await user.send("Не забываем заполнить стендап! Осталось всего 90 минут.")
    except:
        print('notify error')


@notify.before_loop
async def before_notify():
    for _ in range(60 * 60 * 24):
        if dt.datetime.now().strftime("%H:%M") == "10:30" and dt.datetime.now().weekday() < 5:
            print('It is time to notify colleagues about standup')
            return
        await asyncio.sleep(31)


@tasks.loop(hours=24)
async def notify_last():
    try:
        myguild = client.get_guild(bi_rpa_guild)
        list_users = myguild.members

        for user in list_users:
            user_roles = user.roles
            if any(filter(lambda x: x[1].name == 'Производство', enumerate(user_roles))):
                if any(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(user_roles))):
                    print(user.name + " published standup")
                else:
                    print(user.name + " need a reminder")
                    await user.send("До конца стендапа осталось 30 минут. Надо его заполнить!")
    except:
        print('notify_last error')


@notify_last.before_loop
async def before_notify_last():
    for _ in range(60 * 60 * 24):
        if dt.datetime.now().strftime("%H:%M") == "11:30" and dt.datetime.now().weekday() < 5:
            print('It is time to last time notify colleagues about standup')
            return
        await asyncio.sleep(31)

# test
# client.run('MTA5MTMxNTcyMTEwNTA2NDAxNw.GWF5wd.HyujyUNA9RfJX2VT3V_QBQBdiGzKkfjySC7M04')
# prod
client.run('MTA4OTg3MzA1ODY5MDUxNDk3NA.G7jniV.emCqbv0YQFkdVcy6VQ3kUvzbg0GVqU5gXTHYMM')