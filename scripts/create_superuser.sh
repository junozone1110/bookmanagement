#!/bin/bash

# 管理ユーザー作成スクリプト

echo "Creating Django superuser..."

docker-compose -f docker/docker-compose.yml exec app python manage.py createsuperuser

