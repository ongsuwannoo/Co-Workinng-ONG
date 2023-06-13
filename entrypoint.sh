#!/bin/sh
USERNAME="$ADMIN_USERNAME"
EMAIL="$ADMIN_EMAIL"
PASSWORD="$ADMIN_PASSWORD"

python manage.py makemigrations
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$USERNAME', '$EMAIL', '$PASSWORD')" | python manage.py shell
python manage.py loaddata fixtures/initial_data.json
exec "$@"