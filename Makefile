COMPOSE_DEV_FILES := -f docker-compose.yml # -f docker-compose.dev.yml

start:
	docker-compose build
	docker-compose run --rm backend python manage.py migrate
	#docker-compose run --rm backend python manage.py collectstatic --noinput
	docker-compose $(COMPOSE_DEV_FILES) up

test:
	docker-compose run --rm backend python manage.py test --keepdb --verbosity 3

backend-bash:
	docker-compose run --rm backend bash

redis-cli:
	docker-compose run --rm redis redis-cli


TICKER ?= AAPL
AMOUNT ?= 196.89

.PHONY: new-purchased-amount
new-purchased-amount:
	@echo "POST request new purchased amount of ${AMOUNT} for TICKER=${TICKER} to backend."
	./post_request.sh purchased_amount "${TICKER}" "${AMOUNT}"