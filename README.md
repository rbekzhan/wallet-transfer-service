# backend

# Инструкции по установке и запуску проекта

## Клонирование репозитория

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

4. Если миграции еще не были выполнены, создайте их:
    ```bash
   poetry run create_migrate

5. Примените миграции к базе данных:
    ```bash
   poetry run migrate

6. Добавьте данные в базу данных (если необходимо):
    ```bash
    poetry run insert_data
   
7. Запустите сервис:
    ```bash
    poetry run run_api

