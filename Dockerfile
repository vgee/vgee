# Использовать официальный образ Python в качестве базового
FROM python:3.9-slim

# Установить рабочую директорию
WORKDIR /app

# Скопировать файлы проекта в контейнер
COPY . /app

# Установить зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Установить переменные окружения
ENV BOT_TOKEN=your_actual_bot_token_here
ENV DEFAULT_SETTING=your_default_setting_here

# Запустить приложение
CMD ["python", "main.py"]
