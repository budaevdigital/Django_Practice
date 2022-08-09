# Django-Practice.Yandex-Course

![Django Love](_assets/django_love.png)

## Описание

Тренировочный проект на Django.

Сайт-блог, позволяющий публиковать и редактировать посты, добавлять комментарии к постам, подписываться на авторов и сообщества.

Для просмотра примера готового проекта, можно перейти по адресу: https://dmitrybudaev.ru

> P.S. Если сайте не работает, значит сервер был отключен.


## Технологии

- Docker
- Django
- django-debug-toolbar
- djangorestframework
- PostgreSQL
- Pillow
- Gunicorn c Nginx

>Полный список вы можете посмотреть в `requirements.txt` (yatube/requirements.txt)

## ENV - необходимые переменные

- В проекте используется переменные в виртуальном окружении и библиотека dotenv для их загрузки. В директории `yatube`, где расположен файл `settings.py`, создайте новый файл `.env` и пропишите:

```text
GLOBAL_BUILD=False # Если вам нужен Sentry, установите True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<Пароль PostgreSQL>
DB_HOST=127.0.0.1 # Если загружаете на сервер, введите django (имя образа в docker-compose)
DB_PORT=5432
SC_KEY=<Любой сгенерированный пароль для Django>
SENTRY_DNS=<Ваш API ключ в Sentry> # Если нужен мониторинг проекта.
ALLOWED_HOSTS=django 127.0.0.1 0.0.0.0 <ваш.IP.хостинга> <ваше-доменное-имя>
```

> В `ALLOWED_HOSTS` не указываете `*` (разрешить запрос с любых адресов) - это большая проблема для безопасности сайта

- Пароль для `SC_KEY` можно сгенерировать и скопировать из терминала, введя команду:
```
openssl rand -hex 32
```

## Запуск проекта с помощью Docker

> Прежде, чем начать, установите Docker: [Как установить Docker](https://docs.docker.com/engine/install/)

В корневой директории лежат два Docker файла: `docker-compose.local.yml` и `docker-compose.prod.yml`.
Из названия понятно, что **prod** - для сервера, а **local** - для локального разворачивания.

В директории `nginx` лежит Docker файл и конфигурационные файлы для выбранного типа разворачивания.

Для **prod**, в `nginx/prod.conf` не забудьте поменять *настройки IP и домена на свои в файле!*

> Чтобы приступать к сборке - удалите `prod` или `local` в название файла. Должно получится: **docker-compose.yml**. 

После, введите команду для сборки:

```bash
docker-compose up --build
```
Сборка должна пройти без проблем


### Создания суперпользователя

Для начала нужно узнать ID контейнера django:

```bash
docker container ls
```

Скопируйте нужный ID. Затем введите комманду:

```bash
docker exec -it <ID_container> bash # зайдёт в терминал в самом контейнере
```

Следующей командой создадим суперпользователя в самом контейнере:

```bash
python manage.py createsuperuser
```

### Если возникли проблемы с получением SSL-сертификата

> Перед первым запуском обязательно **закомментируйте** указанные блоки в `prod.conf` конфигурации Nginx

Если возникли проблемы с получением сертификата, введите команду при запущенном докере и дождитесь успешного ответа.

```bash
docker-compose run --rm --entrypoint "\
certbot certonly --webroot -w /var/www/certbot \
  # укажите свой email
  --email budaev.digital@yandex.ru \
  # укажите свой домен
  -d dmitrybudaev.ru \
  -d www.dmitrybudaev.ru \
  --rsa-key-size 2048 \
  --agree-tos \
  --force-renewal" certbot
```

После получения успешного ответа, можно раскомментировать блоки `listen 443 ssl;` в `prod.conf` конфигурации Nginx.


## Запуск проекта обычным способом

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