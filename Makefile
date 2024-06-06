COMPOSE_DEV_FILES := -f docker-compose.yml # -f docker-compose.dev.yml

start:
	docker-compose run --rm backend python manage.py migrate
	#docker-compose run --rm backend python manage.py collectstatic --noinput
	docker-compose $(COMPOSE_DEV_FILES) up --build