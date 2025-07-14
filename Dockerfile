# Используем официальный образ Python 3.11
FROM python:3.11-slim as builder

# Устанавливаем переменные окружения для Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /opt/calamine-mcp-server

# Копируем файлы зависимостей и устанавливаем их
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root && rm -rf $POETRY_CACHE_DIR

#-----------------------------------------------------

# Создаем финальный, легковесный образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /opt/calamine-mcp-server

# Копируем виртуальное окружение с зависимостями из сборщика
COPY --from=builder /opt/calamine-mcp-server/.venv ./.venv

# Активируем виртуальное окружение для всех последующих команд
ENV PATH="/opt/calamine-mcp-server/.venv/bin:$PATH"

# Копируем исходный код приложения
COPY ./calamine_mcp ./calamine_mcp

# Запускаем приложение
CMD ["excel-mcp-server"]
