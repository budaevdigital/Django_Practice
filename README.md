# Django-Practice.Yandex-Course

## Описание

Тренировочный проект на Django.

Сайт-блог, позволяющий публиковать и редактировать посты, добавлять комментарии к постам, подписываться на авторов и сообщества.

## Технологии

Django==4.0.4

django-debug-toolbar==3.4.0

djangorestframework==3.13.1

flake8==4.0.1

## Запуск проекта
- Скопируйте файлы проекта в нужную директорию

- Активируйте виртуальное окружение venv в нужной директории
```bash
python -m venv venv
```

- Установите все необходимые библеотеки проекта
```bash
python -m pip install -r requirements.txt
``` 

### Дополнительные настройки

- В проекте используется переменные в виртуальном окружении и библиотека os.environ для их загрузки.

- В директории `yatube`, где расположен файл settings.py, создайте новый файл .env и пропишите:
```
SECRET_KEY=<Ваш_секретный_ключ>
```
- Пароль можно сгенерировать и скопировать из терминала, введя команду:
```
openssl rand -hex 32
```

- Запускаем миграции для настройки полей в базе данных

```bash
python manage.py migrate
```

- Для входа в админку (http://127.0.0.1:8000/admin), необходимо создать суперпользователя:
```bash
python manage.py createsuperuser
```

- Для запуска сервера, в папке с файлом manage.py выполните команду:
```bash
python manage.py runserver
```
- Можете переходить в браузере на http://127.0.0.1:8000/ и играться с проектом :)

