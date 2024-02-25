#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose --no-ansi"

cd /etc/django_app/backend/
$COMPOSE up -d certbot && $COMPOSE restart nginx
