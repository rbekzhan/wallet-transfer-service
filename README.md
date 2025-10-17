# backend

# Инструкции по установке и запуску проекта

## Клонирование репозитория
0. docker compose up (не успел доконца поднят тут только базы поднимаеться)


1. Клонируйте репозиторий:
   ```bash
   git clone <URL репозитория>
   cd <папка проекта>

2. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
   
3. Установите зависимости с помощью Poetry:
    ```bash
   poetry install


4. Примените миграции к базе данных:
    ```bash
   poetry run migrate

   
7. Запустите сервис:
    ```bash
    poetry run run_api

