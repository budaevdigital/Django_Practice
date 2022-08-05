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

- Установите все необходимые зависимости проекта
```bash
python -m pip install -r requirements.txt
``` 

### Дополнительные настройки


> Для запуска проекта потребуется настроенный PostgreSQL!

```bash
sudo -u postgres psql
CREATE DATABASE yatube;
CREATE USER yatube_user WITH ENCRYPTED PASSWORD 'password'; 
GRANT ALL PRIVILEGES ON DATABASE yatube TO yatube_user;
```
- Приложение подготовлено к работе с сервисом мониторинга ошибок `Sentry`, если не планируете его использовать - закомментируйте следующий фрагмент кода в yatube/settings.py:

```bash
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DNS'),
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

- В проекте используется переменные в виртуальном окружении и библиотека dotenv для их загрузки. В директории `yatube`, где расположен файл settings.py, создайте новый файл .env и пропишите:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=yatube
POSTGRES_USER=yatube_user
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