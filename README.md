# Проект "Продуктовый помощник"

Foodgram - это онлайн-платформа, где пользователи могут публиковать, искать и сохранять рецепты. Вы можете создавать свои собственные рецепты, добавлять их в избранное и составлять списки покупок. Также вы можете подписываться на других пользователей и получать обновления о новых рецептах, которые они публикуют.

## Содержание

- [Установка](#установка)
- [Настройка](#настройка)
- [Запуск](#запуск)
- [Использование](#использование)
- [Технологии](#технологии)
- [Докер](#докер)
- [Автор](#автор)
- [Лицензия](#лицензия)

## Установка

- Склонируйте репозиторий:

```bash
git clone https://github.com/romanpittchai/foodgram-project-react.git
```

Перейдите в каталог проекта:
`cd foodgram-project-react`


## Настройка

- Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

- Установите зависимости:

```bash
pip install -r requirements.txt
```

- Создайте файл с переменными окружения `.env` и заполните его необходимыми значениями. Пример файла `.env` можно найти в файле `.env.example`.

- Примените миграции:

```bash
python manage.py migrate
```

- Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

## Запуск

- Запустите сервер разработки:

```bash
python manage.py runserver
```

- Откройте веб-браузер и перейдите по адресу http://localhost:8000 для доступа к приложению Foodgram

## Использование

Приложение Foodgram имеет следующие основные функции:

- Просмотр рецептов: Вы можете просматривать рецепты, искать их по названию или категории, а также просматривать рецепты, опубликованные другими пользователями.
- Создание рецептов: Вы можете создавать свои собственные рецепты, добавлять фотографии, указывать список ингредиентов и пошаговые инструкции.
- Добавление в избранное: Вы можете добавлять рецепты в избранное, чтобы легко найти их позже.
- Составление списка покупок: Вы можете добавлять ингредиенты из рецептов в список покупок, чтобы иметь доступ к нему при походе в магазин.
- Подписка на авторов: Вы можете подписываться на других пользователей и получать обновления о новых рецептах, которые они публикуют.
- Так же доступен hex-генератор по адресу http://localhost/hex/

## Технологии

Foodgram разработан с использованием следующих технологий:

    Python
    Django
    Django REST Framework
    PostgreSQL
    Docker

## Документация

Спецификацию по api проекта, а так же примеры api можно найти по адресу:
http://localhost/api/docs/

## Докер

Проект собирается с помощью докера. Докер-файлы находятся в каждой из ключевых директорий проекта. Проект собирается с помощью `sudo docker-compose up --build -d`. 
Далее необходимо создать миграции, выполнить миграции, создать суперпользователя (если нужно), создать тестового пользователя. Так же необходимо собрать статику и копировать её в 
целевую папку. 
- sudo docker-compose exec <контейнер> <необходимая команда>

Вместе с докер-файлами в проекте присутствуют скрипты .sh
Для frontend'a и nginx'a скрипты выполняются при сборке контейнеров (просто необходимые для удобства отладки пакеты). Для backend'a необходимо выполнить скрипт из командной строки:

```bash
sudo docker compose exec web sh backendjob.sh
```

После будут установлены некоторые пакеты для ОС, созданы и применены миграции, загружены тестовые данные из CSV-файлов, создан суперпользователь, просто тестовый пользователь (все данные для них должны быть приготовлены заранее в env-файле), собрана статика и копирована в целевую папку. 

Отдельно имеется команда, которая очищает от всех данных БД:
```bash
sudo docker compose exec web clearbd
```

Кроме того, для backend'a создан отдельный Makefile, ознакомиться к которым можно в корневой папке приложения backend.

## Автор 

Автор проекта: _Богатырев Роман_

    GitHub: https://github.com/romanpittchai/foodgram-project-react    

## Лицензия

Foodgram доступен под лицензией MIT License.
