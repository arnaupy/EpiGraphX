# Docker compose file namee
DEVELOP_DOCKER_COMPOSE_FILE = develop.yml
TEST_DOCKER_COMPOSE_FILE = test.yml

# Comand after make
COMMAND := $(firstword $(MAKECMDGOALS))

# Message of confirmation for `stop` and `down` comands
ifeq ($(COMMAND), stop)
	CHECK_MESSAGE = Do you want to stop the server?
else 
	CHECK_MESSAGE = Do you want to delete containers, images and volumes in "$(DOCKER_COMPOSE_FILE)" ?
endif

all: create 

# Make file to manage app related comands, documentation and testing
help:
	@echo "create  -> run the docker compose comand to create the project containers, volumes and networks"
	@echo "devrun  -> start the existing server with terminal messages"
	@echo "run     -> start the existing server in detached mode"
	@echo "stop    -> stop the server after the run command"
	@echo "down    -> remove all the containers"
	@echo "test    -> create the containers to test the app and test it"
	 
create:
	@docker compose -f $(DEVELOP_DOCKER_COMPOSE_FILE) create --build

devrun:
	@docker compose -f $(DEVELOP_DOCKER_COMPOSE_FILE) up 

run:
	@docker compose -f $(DEVELOP_DOCKER_COMPOSE_FILE) up -d 

stop: 
	@docker compose -f $(DEVELOP_DOCKER_COMPOSE_FILE) stop

down: 
	@docker compose -f $(DEVELOP_DOCKER_COMPOSE_FILE) down 

test: create-tests run-tests

create-tests:
	@docker compose -f $(TEST_DOCKER_COMPOSE_FILE) create --build 

run-tests:
	@docker compose -f $(TEST_DOCKER_COMPOSE_FILE) up --exit-code-from app-test || true
	@docker-compose -f $(TEST_DOCKER_COMPOSE_FILE) down -v --remove-orphans

__check:
	@echo "$(CHECK_MESSAGE) [y/n] " && read ans && [ $${ans:-y} = y ] 
	
