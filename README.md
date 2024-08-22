# Packagebusters

## Setup
```sh
# Install dependencies
poetry install

# Setup pre-commit hook
poetry run pre-commit install -t pre-commit
```

Необходимые переменные для билда контейнера:
```sh
- GITLAB_TOKEN
- GITLAB_URL
```

Сборка контейнера:
```sh
docker build -t INSERT_YOU_TAG_HERE . --no-cache 
```


## Локальный запуск

1. Создай **.env** файл с переменными

```sh
GITLAB_TOKEN=<value>
GITLAB_URL=<value>
```

2. Подними контейнеры:

```sh
docker-compose up -d --build
```
