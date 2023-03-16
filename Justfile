set dotenv-load := false

@default:
    just --list

shell:
	docker-compose run --rm web bash

rebuild:
	docker-compose rm -f web
	docker-compose build --force-rm web