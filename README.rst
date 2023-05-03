..    include:: <isonum.txt>
Eye Of KSYP
==========

.. image:: https://img.shields.io/pypi/v/discord.py.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord.py.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI supported Python versions

Многоцелевой Discord Бот.

Ключевые Особенности
-------------

- Организация стендапов BI и RPA департамента.
- Публикация несписанных часов КСУП.

Установка
----------

| **Python 3.9**
| **Discord.py 2.2.3**

Для установки библиотеки discord.py нужно выполнить следущую команду:

.. code:: sh

    py -3 -m pip install -U discord.py

Так же используются библиотеки: ``pandas``, ``re``, ``asyncio`` и ``datetime``.

Подключение Скрипта К Боту
~~~~~~~~~~~~~~~~~~

#. Войти в `личный кабинет <https://discord.com/developers/applications>`__ разработчика Discord.
#. Создать Application с ботом внутри.
#. Получить токен бота.
#. Выдать боту права на ``PRESENCE INTENT``, ``SERVER MEMBERS INTENT``, ``MESSAGE CONTENT INTENT``.
#. Пригласить бота на нужный сервер. Для этого можно использовать вкладку OAuth2 → URL Generator.
#. Ставим галочки Scopes → bot и Bot Permissions → Administrator.
#. Переходим по созданной ссылке и добавляем бота на сервер.

Полученный токен необходимо указать в скрипте, в последней строке.

.. code:: python

    client.run('token')

Ссылки
------

- `Документация discord.py <https://discordpy.readthedocs.io/en/latest/index.html>`_
- `Discord API <https://discord.gg/discord-api>`_