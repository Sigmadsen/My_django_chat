#!/bin/bash
# Apply migrations
docker compose exec web python manage.py migrate --noinput

# Run tests in docker container
docker compose exec web python manage.py test