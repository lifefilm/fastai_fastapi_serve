# Команды для быстрой работы с docker-compose
# за основу https://gist.github.com/fortunto2/0f77af5edde7a5c5c9ee3930e18dd25d
.PHONY: help prod


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

# Соединяем 2 файла для prod, и сохраняем в переменной
prod_compose_file = -f docker-compose.prod.yml

# # Задаем по умолчанию environment
export TAG=dev
export PORT_DJANGO=5004

%:
	@:

prod = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

ttt:
	@echo $(prod)


local: ## Запускает джангу по адрессу uvicorn
	uvicorn main:app --reload

login: ## Авторизоваться в регистре gitlab
	@docker login registry.gitlab.com

build: ## Сбилдить проект
    @req
	docker-compose build

push: ## Закачать в ригистр сбилдинные образы
	@docker-compose push

pull: ## Скачать из регистра последний образ
	@docker-compose pull

req: requirements.txt generate
    @pipenv lock -r > requirements.back.txt




clear-pyc: ## Очистка pyc файлов, иногда нужно для запуска тестов
	@find . \( -name '__pycache__' -or -name '*.pyc' \) -delete

down: ## Остановить сервисы
	@docker-compose down

restart: ## Рестартануть все сервисы
	@docker-compose restart


# TESTS

test: ## Запуск тестов
	@docker-compose run --rm api pytest -s


# MAIN

# Быстрая команда: сбилдить и залить в регистр
bp: build push

up: ## Запустить приложение в Dev среде (для разработки локально)
	@docker-compose up -d

upb: ## Запустить и сбилдить
	@docker-compose up -d --build

upd: down migrate up

ps:  ## Посмотреть запущенные
	@docker-compose ps

lint: ## Статический анализ кода
	@docker-compose run --rm django flake8
