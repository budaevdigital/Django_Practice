#!/bin/bash
# if [ "$DB_NAME" = "yatube" ]
# then
#     echo "Ждём пока подключится Postgres..."

#     while  ! nc -z $DB_HOST $DB_PORT; do
#         sleep 0.5
#     done

#     echo "Postgres запущен!"
# fi

# python manage.py migrate
# python manage.py collectstatic --no-input --clear

# exec "$@"