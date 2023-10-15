# Docker compose file name
DOCKER_COMPOSE_FILE = docker-compose-dev.yml

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
	@echo "build  -> run the docker compose comand to build the project containers and run it"
	@echo "devrun -> start the existing server with terminal messages"
	@echo "run    -> start the existing server in detached mode"
	@echo "stop   -> stop the server after the run command"
	@echo "down   -> remove all the containers, images and volums"
	 
build:
	@docker compose -f $(DOCKER_COMPOSE_FILE) up --build

devrun:
	@docker compose -f $(DOCKER_COMPOSE_FILE) up 

run:
	@docker compose -f $(DOCKER_COMPOSE_FILE) up -d

stop: __check
	@docker compose -f $(DOCKER_COMPOSE_FILE) stop

down: __check
	@docker compose -f $(DOCKER_COMPOSE_FILE) down --volumes --rmi all


__check:
	@echo "$(CHECK_MESSAGE) [y/n] " && read ans && [ $${ans:-y} = y ] 
	
