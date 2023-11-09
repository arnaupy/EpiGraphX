# Docker compose file name
DOCKER_COMPOSE_FILE = docker-compose-dev.yml
DOCKER_COMPOSE_FILE_TESTS = docker-compose-tests.yml
DATABASE_VOLUME_NAME = postgres-data
APP-DATABASE_NETWORK_NAME = app-data

# Comand after make
COMMAND := $(firstword $(MAKECMDGOALS))

# Message of confirmation for `stop` and `down` comands
ifeq ($(COMMAND), stop)
	CHECK_MESSAGE = Do you want to stop the server?
else 
	CHECK_MESSAGE = Do you want to delete containers, images and volumes in "$(DOCKER_COMPOSE_FILE)" ?
endif

# Make file to manage app related comands, documentation and testing
help:
	@echo "create  -> run the docker compose comand to create the project containers, volumes and networks"
	@echo "devrun  -> start the existing server with terminal messages"
	@echo "run     -> start the existing server in detached mode"
	@echo "stop    -> stop the server after the run command"
	@echo "down    -> remove all the containers, images and volums"
	@echo "test    -> create the containers to test the app and test it"
	 
create:
	@docker volume create $(DATABASE_VOLUME_NAME)
	@docker network create $(APP-DATABASE_NETWORK_NAME)
	@docker compose -f $(DOCKER_COMPOSE_FILE) create

devrun:
	@docker compose -f $(DOCKER_COMPOSE_FILE) up 

run:
	@docker compose -f $(DOCKER_COMPOSE_FILE) up -d

stop: __check
	@docker compose -f $(DOCKER_COMPOSE_FILE) stop

down: __check
	@docker compose -f $(DOCKER_COMPOSE_FILE) down 
	@docker volume rm $(DATABASE_VOLUME_NAME)
	@docker network rm $(APP-DATABASE_NETWORK_NAME)

test:
	@docker-compose -f $(DOCKER_COMPOSE_FILE_TESTS) down -v
	@docker compose -f $(DOCKER_COMPOSE_FILE_TESTS) up --abort-on-container-exit 


__check:
	@echo "$(CHECK_MESSAGE) [y/n] " && read ans && [ $${ans:-y} = y ] 
	
