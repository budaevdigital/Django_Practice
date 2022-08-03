# Django-Practice.Yandex-Course

![Django Love](_assets/django_love.png)

## Описание

Тренировочный проект на Django.

Для просмотра примере готового проекта, можно перейти по адресу:

```text
https://django.hopto.org
```
P.S. Если сайте не работает, значит сервер был отключен.

Сайт-блог, позволяющий публиковать и редактировать посты, добавлять комментарии к постам, подписываться на авторов и сообщества.

## Технологии

Django

django-debug-toolbar

djangorestframework

PostgreSQL

Pillow

Gunicorn c Nginx

>Полный список вы можете посмотреть в `requirements.txt` (yatube/requirements.txt)

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

> Для запуска проекта потребуется настроенный PostgreSQL!

- В директории `yatube`, где расположен файл settings.py, создайте новый файл .env и пропишите:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<Имя базы в PostgreSQL>
POSTGRES_USER=<Пользователь PostgreSQL>
POSTGRES_PASSWORD=<Пароль PostgreSQL>
DB_HOST=127.0.0.1
DB_PORT=5432
SC_KEY=<Любой сгенерированный пароль для Django>
SENTRY_DNS=<Ваш API ключ в Sentry> # Если нужен мониторинг проекта. Можно убрать
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

> Не забудьте поменять IP сервера на свой в настройках `settings.py`
```python
ALLOWED_HOSTS = [
    'ваш домен',
    'ваш IP хостинга',
    ...
]
```

- Для верности, можно перегрузить настроенный `nginx` и `gunicorn`:
```bash
sudo systemctl reload nginx
sudo systemctl restart gunicorn
```

Всё! Проект должен быть готов к запуску.