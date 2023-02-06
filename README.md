# Foodgram - инстаграм из мира рецептов

Изучайте авторские кулинарные шедевры и делитесь собственными :)
*"Сытый считает звезды на небе, а голодный думает о хлебе"*.

### Технологии

* Python 3.10
* Django 4.1
* DjangoRestFramework 3.14
* Djoser 2.1
* Pdfkit 1.0

### Приложение

Продуктовый помощник Foodgram позволяет пользователям публиковать собственные рецепты, добавлять чужие в избранное и подписываться на публикации других авторов. Сервис «Список покупок» генерирует список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Установка

- Клонируйте репозиторий
```
git clone <link>
```

- Создайте и активируйте виртуальное окружение
```
python -m venv venv
```

- Перейдите в папку `infra`, создайте файл `.env`, добавьте соответствующие константы
```
DJANGO_SECRET_KEY=<value>

DB_ENGINE=django.db.backends.postgresql
DB_NAME=<value>
DB_USER=<value>
DB_PASSWORD=<value>
DB_HOST=<value>
DB_PORT=<value>
```

- Перейдите в папку `backend`, установите зависимости
```
pip install -r requirements.txt
```

- Примените миграции
```
python manage.py migrate
```

- Наполните БД ингредиентами
```
python manage.py add_ingredients
```

- Создайте суперпользователя
```
python manage.py createsuperuser
```

- Запустите проект
```
python manage.py runserver
```

### Список доступных эндпойнтов

* `users` - управление пользователями;
* `auth` - аутентификация пользователей;
* `ingredients` - ингредиенты;
* `recipes` - рецепты;
* `tags` - теги;
* `recipes/{id}/shopping_cart/` - список покупок;
* `recipes/{id}/favorite/` - избранное;
* `users/{id}/subscribe/` - подписки.

Для доступа к документации API установите **Docker**, перейдите в папку `infra` и выполните команду:
```
sudo docker-compose up -d
```

Документация станет доступна по адресу: *http://localhost/api/docs/redoc.html*.

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

### В следующем релизе

* Наполнение проекта, создание фикстур;
* Развертывание в контейнерах;
* Деплой на сервер.

### Автор

*Чупринский Станислав*
