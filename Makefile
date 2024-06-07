COMPOSE_DEV_FILES := -f docker-compose.yml # -f docker-compose.dev.yml

start:
	docker-compose build
	docker-compose run --rm backend python manage.py migrate
	#docker-compose run --rm backend python manage.py collectstatic --noinput
	docker-compose $(COMPOSE_DEV_FILES) up

backend-bash:
	docker-compose run --rm backend bash

redis-cli:
	docker-compose run --rm redis redis-cli