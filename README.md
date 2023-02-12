![Foodgram workflow](https://github.com/stas-chuprinskiy/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Foodgram - инстаграм в мире рецептов

Изучайте авторские кулинарные шедевры и делитесь собственными :)

*"Сытый считает звезды на небе, а голодный думает о хлебе"*.

Проект доступен по адресу: [foodgram.chupss.me](https://foodgram.chupss.me)

### Технологии

* Python 3.10
* Django 4.1
* DjangoRestFramework 3.14
* Django-filter 22.1
* Django-extra-fields 3.0
* Djoser 2.1
* Wkhtmltopdf 0.12.4

### Приложение

Продуктовый помощник Foodgram позволяет пользователям публиковать собственные рецепты, добавлять чужие в избранное и подписываться на публикации других авторов. Сервис «Список покупок» генерирует список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Установка

> Для развертывания и тестирования проекта необходимо установить [Docker](https://docs.docker.com/engine/install/)

- Клонируйте репозиторий:
```
git clone <link>
```

- Перейдите в папку `/infra`, создайте файл `.env`, определите соответствующие константы:
```
DJANGO_SECRET_KEY=<value>

POSTGRES_DB=<value>
POSTGRES_USER=<value>
POSTGRES_PASSWORD=<value>
HOST=database
PORT=5432
```

- Выполните сборку проекта:
```
docker-compose up -d
```

- Примените миграции:
```
docker-compose exec foodgram_backend python manage.py migrate
```

- Загрузите фикстуры:
```
docker-compose exec foodgram_backend python manage.py loaddata fixtures/inital_data.json

docker-compose exec foodgram_backend cp -r fixtures/img/ media/
```

- Соберите статические файлы бэкенда:
```
docker-compose exec foodgram_backend python manage.py collectstatic --no-input
```

- Создайте суперпользователя (при необходимости):
```
docker-compose exec foodgram_backend python manage.py createsuperuser
```

Станут доступны:
* фронтенд - по адресу `localhost`;
* API - по адресу `localhost/api/`;
* документация API - по адресу `localhost/api/docs/`.

### Список доступных эндпойнтов API

* `users` - управление пользователями;
* `auth` - аутентификация пользователей;
* `ingredients` - ингредиенты;
* `recipes` - рецепты;
* `tags` - теги;
* `recipes/{id}/shopping_cart/` - список покупок;
* `recipes/{id}/favorite/` - избранное;
* `users/{id}/subscribe/` - подписки.

### Пользовательские роли

- **Аноним** — создание аккаунта, просмотр рецептов на главной, просмотр отдельных страниц рецептов, просмотр страниц пользователей, фильтрация рецептов по тегам.
- **Аутентифицированный пользователь (user)** — Аноним + вход/выход, смена пароля, создание/редактирование/удаление собственных рецептов, работа с персональным списком избранных рецептов, работа с персональным списком покупок + скачивание в формате `pdf`, подписка/отписка на авторов, просмотр страницы подписок.
- **Администратор (admin)** — Аутентифицированный пользователь + изменение пароля любого пользователя, создание/блокировка аккаунтов пользователей, редактирование/удаление любых рецептов, создание/редактирование/удаление ингредиентов и тегов.

### Алгоритм регистрации новых пользователей

1. Отправка POST-запроса с параметрами `email`, `username`, `first_name`, `last_name` и `password` на эндпоинт `/api/users/` 
2. Отправка POST-запроса с параметрами `email` и `username` на эндпоинт `/api/auth/token/login/`, получение токена авторизации.

После получения токена авторизации можно отправлять запросы к сервису.

### Тестирование API

Вы можете отправлять запросы к API любым удобным для вас способом. 
В примерах ниже для отправки запросов используется библиотека `httpie`. 
Подробней о `httpie` вы можете узнать в [документации](https://httpie.io/docs/cli).

**Регистрация**
```
http -v POST 127.0.0.1:8000/api/users/
email="<email>" username="<username>" password="<password>" first_name="first_name" last_name="last_name"
```

```
{
    "email": "<email>",
    "id": <id>,
    "username": "<username>",
    "first_name": "<first_name>",
    "last_name": "<last_name>"
}
```

**Получение токена авторизации**
```
http -v POST 127.0.0.1:8000/api/auth/token/login/
email="<email>" password="<password>"
```

```
{
    "auth_token": "<token>"
}
```

**Получение списка ингредиентов**
```
http -v GET 127.0.0.1:8000/api/ingredients/
Authorization:"Token <token>"
```

```
[
    {
        "id": <id>,
        "name": "<name>",
        "measurement_unit": "<measurement_unit>"
    },
    ...
]
```

**Создание рецепта**
```
http -v POST 127.0.0.1:8000/api/recipes/
Authorization:"Token <token>" 
tags=[<id>] ingredients=[{"id": <id>, "amount": <amount>}] name="<name>" image="<image>" text="<text>" cooking_time="<cooking_time>"
```

```
{
    "count": <count>,
    "next": "<next>",
    "previous": "<previous>",
    "results": [
        {
            "id": <id>,
            "tags": [
                {
                    "id": <id>,
                    "name": "<name>",
                    "color": "<color>",
                    "slug": "<slug>"
                }
            ],
            "author": {
                "email": "<email>",
                "id": <id>,
                "username": "<username>",
                "first_name": "<first_name>",
                "last_name": "<last_name>",
                "is_subscribed": <is_subscribed>
            },
            "ingredients": [
                {
                    "id": <id>,
                    "name": <name>,
                    "measurement_unit": <measurement_unit>,
                    "amount": <amount>
                }
            ],
            "is_favorited": <is_favorited>,
            "is_in_shopping_cart": <is_in_shopping_cart>,
            "name": "<name>",
            "image": "<image>",
            "text": "<text>",
            "cooking_time": <cooking_time>
        }
    ]
}
```

**Добавление рецепта в список покупок**
```
http -v POST 127.0.0.1:8000/api/recipes/{id}/shopping_cart/
Authorization:"Token <token>"  
```

```
{
    "id": <id>,
    "name": "<name>",
    "image": "<image>",
    "cooking_time": <cooking_time>
}
```

**Скачивание списка покупок**
```
http -v GET 127.0.0.1:8000/api/recipes/download_shopping_cart/
Authorization:"Token <token>"  
```

### Автор

*Чупринский Станислав*
