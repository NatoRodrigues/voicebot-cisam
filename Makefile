current_dir := $(shell pwd)
user := $(shell whoami)

ENDPOINTS = endpoints/docker-endpoints.yml
CREDENTIALS = credentials/credentials.yml
CREDENTIALS_TELEGRAM = credentials/telegram-credentials.yml 
clean:
	docker-compose down
	cd bot/ && make clean

stop:
	docker-compose stop


############################## BOILERPLATE ##############################
first-run:
	make build
	make train
	make shell

build:
	make build-bot

build-bot:
	docker-compose build \
		--no-cache bot

shell:
	docker-compose run \
		--rm \
		--service-ports \
		bot \
		make shell ENDPOINTS=$(ENDPOINTS)

actions:	
	docker-compose run \
		-d \
		--rm \
		--service-ports \
		bot \
		make actions

webchat:
	echo "Executando Bot com Webchat."
	docker-compose run \
		-d \
		--rm \
		--service-ports \
		bot \
		make webchat ENDPOINTS=$(ENDPOINTS) CREDENTIALS=$(CREDENTIALS)
	docker-compose up \
		-d \
		webchat
	echo "Acesse o WEBCHAT em: http://localhost:5010"

telegram:
	docker-compose run \
		-d \
		--rm \
		--service-ports \
		bot-telegram \
		make telegram ENDPOINTS=$(ENDPOINTS) CREDENTIALS=$(CREDENTIALS_TELEGRAM)

train:
	docker-compose run \
		--rm bot \
		make train

alltrain:
	make clean 
	sudo service docker start
	make train
	make shell

allweb:
	make clean 
	sudo service docker start
	make train
	make webchat

voicebot:
	make clean 
	sudo service docker start
	make train
	make webchat
	python3 voicebot.py

############################## TESTS ##############################
validate:
	docker-compose run \
		--rm bot \
		make validate

test:
	docker-compose run \
		--rm bot \
		make test

test-nlu:
	docker-compose run \
		--rm \
		bot \
		make test-nlu

test-core:
	docker-compose run \
		--rm \
		bot \
		make test-core

