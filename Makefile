COMPOSE_DEV_FILES := -f docker-compose.yml

start:
	docker-compose build
	docker-compose run --rm backend python manage.py migrate
	#docker-compose run --rm backend python manage.py collectstatic --noinput
	docker-compose $(COMPOSE_DEV_FILES) up

test:
	TARGET=development docker-compose build backend
	docker-compose run --rm backend python manage.py test --keepdb --verbosity 3

backend-bash:
	docker-compose run --rm backend bash

redis-cli:
	docker-compose run --rm redis redis-cli


.PHONY: new-purchased-amount
new-purchased-amount:
	./post_request.sh purchased_amount "${TICKER}" "${AMOUNT}"

.PHONY: crawler
crawler:
	./post_request.sh request_scrapyd "${TICKER}"