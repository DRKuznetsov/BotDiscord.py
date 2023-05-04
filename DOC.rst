Eye Of KSYP Разбор Процесса
==========

| Данный документ является подробным описанием работы скрипта.

Переменные
----
| Объявление переменных.

- ``bi_rpa_guild`` - Идентификатор сервера.
- ``su_report`` - Идентификатор канала для отправки заполненных стендапов.
- ``su_send`` - Идентификатор канала для отправки объявления о начале стендапа.

.. code:: python

    bi_rpa_guild = 1088107116042129548
    su_report = 1088350602150543380
    su_send = 1088447246560935986

Классы
----

StandUpModal
~~~~
| Объявление класса ``StandUpModal()``.
- ``Modal`` - всплывающее окно с настраиваемыми элементами.

.. code:: python

    class StandUpModal(Modal, title="Стендап"):

| Создание текстовых полей.

.. code:: python

    su_com = TextInput(
        # Тип текстового поля. short - однострочный, long - многострочный.
        style=discord.TextStyle.short,
        # Заголовок, название текстового поля.
        label="Есть ли коммерческие задачи на сегодня?",
        # Текст отображаемый внутри текстового поля.
        placeholder="Да/Нет",
        # Максимальная длина текста в поле.
        max_length=16,
        # Является ли поле обязательным.
        required=True
    )

| Объявление события происходящего при отправке заполненного ``Modal``.
- ``interaction`` - переменная описывающая текущее взаимодействие с ``Modal``.

.. code:: python

    async def on_submit(self, interaction: discord.Interaction):

| Описание действий при отправке ``Modal``.

.. code:: python

    # Вывод в консоль сообщения о начале обработки Modal от конкретного пользователя.
    print("Обработка Стендапа От " + interaction.user.name)
    # Получение канала для отправки отчета.
    channel = client.get_channel(su_report)

| Создание отчета в виде ``Embed``.
- ``Embed`` - сообщение с настраиваемыми UI элементами.

.. code:: python

    # Получение цвета пользователя.
    usercolor = await client.fetch_user(interaction.user.id)
    # Создание Embed.
    embed = discord.Embed(title="Стендап", color=usercolor.accent_color)
    # Указание автора текущего взаимодействия.
    embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
    # Заполнение Embed элементами из Modal.
    embed.add_field(name="Коммерческая задача:", value=str(self.su_com), inline=True)
    embed.add_field(name="Руководитель по задачам:", value=str(self.su_pm), inline=True)
    embed.add_field(name="План на сегодня:", value=str(self.su_content), inline=False)
    # Отправка отчета в виде Embed.
    await channel.send(embed=embed)

| Данная конструкция отправляет клиенту пользователя уведомлениие об обработке ``Modal``.
| Если не прислать уведомление, пользователь увидит ошибку. Сам ``Modal`` будет обработан.

.. code:: python

    try:
        await interaction.response.send_message()
    except:
        print("Стендап Обработан От " + interaction.user.name)

| Присвоение роли и отправка отчета автору стендапа.

.. code:: python

    # Получение сервера.
    myguild = client.get_guild(bi_rpa_guild)
    # Получение списка ролей сервера.
    allroles = myguild.roles
    try:
        # Поиск идентификатора роли Золотой Человек.
        idx_role = next(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(allroles)))[0]
        # Получение роли.
        myrole = allroles[idx_role]
        # Получение пользователя, заполнившего стендап.
        iduser = interaction.user.id
        user = myguild.get_member(int(iduser))
        # Присвоение роли пользователю.
        await user.add_roles(myrole)
        # Отправка отчета в личные сообщения.
        await user.send(embed=embed)
    except:
        # В случае ошибки в консоль выведется сообщение.
        print("Can Not Assign Role")

PersistentView
~~~~
| View - способ представления UI элементов в Discord.
| Данный класс реализует две задачи:
#. Добавление в сообщение программируемой кнопки.
#. В случае, если скрипт перезапускается, работа кнопки продолжится. Нет необходимости отправлять сообщение снова.

| Объявление класса ``PersistentView()``.

.. code:: python

    class PersistentView(discord.ui.View):

| Реализация класса.

.. code:: python

    # Кнструктор.
    def __init__(self):
        # Отключение тайм-аута.
        super().__init__(timeout=None)
    # Создание элемента кнопки внутри View. custom_id необходим для переподключения бота к кнопке после перезапуска.
    @discord.ui.button(label='Выступить', style=discord.ButtonStyle.blurple, custom_id='persistent_view:blurple')
    async def blurple(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Отправка Modal в случае взаимодествия с кнопкой.
        await interaction.response.send_modal(StandUpModal())

PersistentViewBot
~~~~
| Класс для создания самого экземпляра бота.
| Объявление класса ``PersistentViewBot()``.

.. code:: python

    class PersistentViewBot(commands.Bot):

| Реализация конструктора.

.. code:: python

    def __init__(self):
        # Определяет объем полномочий бота.
        intents = discord.Intents.default()
        # Полномочия на получение информации о пользователях.
        intents.members = True
        # Полномочия на получение текста сообщений.
        intents.message_content = True
        # Инициализация бота с указанными полномочиями.
        # Указание префикса команд. Не используется, но возможно понадобится в будущем.
        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

| Непосредственное переподключение к ранее созданным ``View``.

.. code:: python

    async def setup_hook(self) -> None:
        self.add_view(PersistentView())

| Данные блок выполняется при событии запуска бота.

.. code:: python

    async def on_ready(self):
        # Запуск задач с расписанием.
        standup.start()
        standup_end.start()
        ksyp.start()
        notify.start()
        notify_last.start()
        # Сообщение в консоль об успешной авторизации бота.
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

Задачи
----
| Задачи - методы выполняющиеся по заданному расписанию.
| Шаблон задачи с расписанием.

.. code:: python

    # Объявление задачи. Выполняется раз в 24 часа.
    @tasks.loop(hours=24)
    async def method(): ...

    # Объявление расписания задачи.
    # Когда данный метод закончит работу, начнется выполнение задачи.
    @method.before_loop
    async def before_method(): ...

standup
~~~~
| Данная задача начинает стендап в 9:00, каждый будний день.
| Реализация расписания. Рассмотрим только это расписание. Остальные строятся точно по такому же принципу.

.. code:: python

    # Цикл на колличество секунд в одном дне.
    for _ in range(60 * 60 * 24):
        # Условие при котором расписание должно закончить работу.
        if dt.datetime.now().strftime("%H:%M") == "09:00" and dt.datetime.now().weekday() < 5:
            # Сообщение о том что задача будет начата.
            print('It is time for standup')
            # Завершение расписания.
            return
        # Ожидание, если условние не выполнилось.
        await asyncio.sleep(31)

| Реализация задачи.

.. code:: python

    myguild = client.get_guild(bi_rpa_guild)
    allroles = myguild.roles
    try:
        idx_role = next(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(allroles)))[0]
        myrole = allroles[idx_role]
        # Удаляем роль Золотой Человек.
        # Нужно для обнуления отображения людей заполнивших стендап в прошлый раз.
        await myrole.delete()
    except:
        print("Role Not Found")
    # Пересоздание роли.
    await myguild.create_role(name="Золотой Человек", color=discord.Colour.gold())
    # Текст сообщения.
    text = "@everyone Время для утреннего стендапа!"
    channel = client.get_channel(su_send)
    # Отправка сообщения с текстом и View.
    await channel.send(text, view=PersistentView())
    su_channel = client.get_channel(su_report)
    await su_channel.send(content='<@&1088108846775554128> Новый день - Новый стендап!')

notify и notify_last
~~~~
| Задачи для отправки напоминания о скором закрытии стендапа. Имеют схожую реализацию, рассмотрим только ``notify``.

.. code:: python

    try:
        myguild = client.get_guild(bi_rpa_guild)
        # Получение списка участников сервера.
        list_users = myguild.members
        # Цикл по каждому участнику.
        for user in list_users:
            # Получение всех ролей участника.
            user_roles = user.roles
            # Проверка необходимости заполнения стендапа пользователю.
            if any(filter(lambda x: x[1].name == 'Производство', enumerate(user_roles))):
                # Проверка заполнил ли пользователь стендап на текущий момент.
                # Вывод в консоль статуса стендапа пользователя.
                if any(filter(lambda x: x[1].name == 'Золотой Человек', enumerate(user_roles))):
                    print(user.name + " published standup")
                else:
                    print(user.name + " need a reminder")
                    # Отправка сообщения пользователю, если стендап не заполнен.
                    await user.send("Не забываем заполнить стендап! Осталось всего 90 минут.")
    except:
        print('notify error')

standup_end
~~~~
| Задача завершающая стендап.

.. code:: python

    limit = 0
    my_channel = client.get_channel(su_send)
    # Получение количества сообщений в канале.
    async for _ in my_channel.history(limit=None):
        limit += 1
    # Удаление сообщений канала в количестве равном limit.
    await my_channel.purge(limit=limit)

ksyp
~~~~
| Данная задача отправляет отчет о несписанных часах в КСУП.
| Рассмотрим только взаимодействие с ботом, поскольку работа с ``dataframe`` и Excel достаточно тривиальна.
| Создание наполнения сообщений.

.. code:: python

    # Получение списка пользователей.
    list_users = client.users
    # Сообщение с упоминаниями.
    tagline = ''
    # Сообщение с пользователями, которых не получится упомянуть.
    non_tagline = ''
    for name in names:
        try:
            # Получение имени из отчета.
            new_name = re.findall("\w*", name)[2] + ' ' + re.findall("\w*", name)[0]
            # Поиск имени среди пользователей.
            id = next(filter(lambda x: x[1].name == new_name, enumerate(list_users)))[0]
            # Добавление пользователя в сообщение с упоминанием.
            tagline = tagline + '<@!' + str(list_users[id].id) + '> '
        except:
            # Добавление пользователя в сообщение с без упоминания.
            non_tagline = non_tagline + re.findall("\w*", name)[2] + ' ' + re.findall("\w*", name)[0] + '; '

| Отправка созданных сообщений. Максимальная длина сообщения бота 2000 символов.

.. code:: python

    # Отправка заголовочного сообщения.
    await channel.send(content='Око КСУП следит за вами')
    # Отправка первых 2000 символов отчета.
    await channel.send(stringdflong[0:2000])
    lgth = len(stringdflong)
    counter = 2000
    # Отправка оставшегося отчета сообщениями по 2000 символов.
    while (counter < lgth):
        stringdf = stringdflong[counter:counter + 2000]
        await channel.send(content=stringdf)
        counter += 2000
    # Отправка сообщения с упомянаниями.
    await channel.send(content=tagline)
    # Отправка сообщения без упомянаний, если есть неопознанные пользователи.
    if non_tagline != '':
        await channel.send(content="Я не смог вас отметить, но знайте я все вижу: " + non_tagline)