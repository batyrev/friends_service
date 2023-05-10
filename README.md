# friends_service

## Requirements
Python 3.9.0+

## Usage
Запуск сервера.

Установка зависимостей:
```
pip install -r requirements.txt
```

Запуск сервера
```
python manage.py runserver
```

## Running with Docker

```bash
# building the image
docker build -t friends_service .

# starting up a container
docker run friends_service

```