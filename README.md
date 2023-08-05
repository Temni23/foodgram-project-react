### Адрес сервера: [Кликнуть по ссылке](https://foodgram-klimov.ddns.net/)
### Логин администратора: superuser
### Пароль администратора: superuser

#  Foodgram

## О проекте

В данном проекте реализована мини соцсеть для обмена рецептами между пользователями

## Технологии
Python 3.11.1, Django 4.1, Django REST framework, React, Docker, Nginx

## Запуск проекта на локальном компьютере

Для запуска проекта необходимо иметь на установленные: node.js, python, pip.

клонировать проект:
git clone git@github.com:Temni23/foodgram-project-react.git
frontend:
cd frontend
npm i
rpm run dev

backend:
cd backend
python -m venv venv

# Linux/macOS:
```
  source env/bin/activate
  ```
# windows:
  ```
  source venv/Scripts/activate
  ```

```
pip install -r requirements.txt
```
```
python manage.py migrate
```
```
python manage.py runserver
```
При успешном старте получим backend приложение на 127.0.0.1:8080

## Альтернативная установка возможна при налиичи на локальом компьютере Docer compose

Запустите проект из корня с помощью команды:
```
docker compose up
```
Соберите статику Django с помощью команды:
```
docker compose exec backend python manage.py collectstatic
```
Скопируйте статику командой:
```
docker compose exec backend cp -r /app/collected_static/. /static/static/
```
По адресу http://127.0.0.1:8080/ сайт будет доступен.


### Автор проекта А.В. Климов

