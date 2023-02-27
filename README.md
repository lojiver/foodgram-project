### Проект foodgram:

Проект foodgram - это социальная сеть для публикации рецептов. Можно подписываться на авторов и следить за публикуемыми ими рецептами, добавлять рецепты в список покупок и распечатывать его перед походом в магазин.

![workflow](https://github.com/lojiver/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Как запустить проект:

Проект доступен на http://158.160.40.57/
(если там ничего нет, значит, я отключила виртуальную машину на Облаке, чтобы она не ела ресурсы)

логин и пароль от админки
gorbunova_ann@mail.ru
koshka

### На локальной машине:
Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/lojiver/foodgram-project-react
```

```
cd infra
```

Собрать и запустить контейнер

```
docker-compose up -d --build 
```

### Шаблон наполнения .env-файла:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=name
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432

### Примеры запросов:

Вывод рецептов:
```
http://localhost/api/recipes/?page=1&limit=6
```

Вывод подписок:
```
http://localhost/api/users/subscriptions/?recipes_limit=1
```

Добавление рецепта:
```
POST
http://localhost/api/recipes/
{
  "ingredients": [
    {
      "id": 58,
      "amount": 15
    },
    {
      "id": 58,
      "amount": 100
    }
  ],
  "tags": [
    3
  ],
  "image": "data:image/jpeg;base64,/9j/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09",
  "name": "Самое блюдо из овощей4",
  "text": "Быстро и просто",
  "cooking_time": 25
}

```



