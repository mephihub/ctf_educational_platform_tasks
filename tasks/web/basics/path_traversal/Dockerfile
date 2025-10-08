# Dockerfile
FROM python:3.11-slim

# Устанавливаем системные утилиты (минимально)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только то, что нужно для установки зависимостей (оптимизация слоёв)
COPY requirements.txt ./

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект (app.py, init_db.py, templates/ и т.д.)
COPY . /app

# Порт приложения
EXPOSE 5000

# Запуск: если базы нет — инициализируем, затем запускаем приложение
# Используем sh -c, чтобы условие работало корректно.
CMD ["sh", "-c", "if [ ! -f ./idor_task.db ]; then echo 'Initializing DB...'; python init_db.py; fi && echo 'Starting app...' && python app.py"]

