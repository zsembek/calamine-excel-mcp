# Используем официальный образ Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /opt/calamine-mcp-server

# Устанавливаем переменные окружения, чтобы избежать вывода логов в буфер
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Устанавливаем системные зависимости
# build-essential нужен для компиляции некоторых зависимостей python-calamine
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы с зависимостями и структурой проекта
COPY requirements.txt pyproject.toml ./

# Устанавливаем зависимости. Этот шаг будет кэшироваться Docker'ом,
# если requirements.txt не изменится, что ускорит последующие сборки.
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код нашего приложения
COPY ./calamine_mcp ./calamine_mcp

# Устанавливаем наше приложение в режиме редактирования.
# Это зарегистрирует команду `excel-mcp-server`, определенную в pyproject.toml
RUN pip install -e .

# Задаем переменные окружения для сервера из вашего docker-compose
# Значения по умолчанию, которые могут быть переопределены в docker-compose.yml
ENV EXCEL_FILES_PATH=/app/backend/data/uploads
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_PORT=8000

# Создаем директорию для загрузок, чтобы избежать проблем с правами
# Пользователь будет задан в docker-compose.yml
RUN mkdir -p ${EXCEL_FILES_PATH} && chown -R 1000:1000 ${EXCEL_FILES_PATH}

# Команда для запуска сервера. `excel-mcp-server` - это точка входа,
# определенная в pyproject.toml, `sse` - это команда в cli.py
CMD ["excel-mcp-server", "sse"]
