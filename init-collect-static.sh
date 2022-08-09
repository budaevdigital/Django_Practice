#!/bin/bash
set -e

python ./yatube/manage.py collectstatic --noinput
