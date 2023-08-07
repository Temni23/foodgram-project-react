###  [Работающий демонстрационный сервер с сайтом](https://foodgram-klimov.ddns.net/)

#  Foodgram

## О проекте
Это учебный дипломный проект выпускника ЯндексПрактикума по специальности Python разработчик.

В данном проекте реализована мини соцсеть для обмена рецептами между пользователями.

Мною подготовлен бэкэнд проекта. Фронтэнд используется стандартный из репозитория ЯндексПрактикума. Проект упакован в образы докер. Выполнен деплой на удаленный сервер.

Посредством git-actions реализовано тестирование, пересборка докер образов на dockerhub, автоматический деплой на удаленный сервер, применение миграций и перезапуск сервера после внесения изменений.

## Технологии
Python 3.9, Django 3.2.16, Django REST framework 3.12.4, React, Docker, Nginx

## Запуск проекта на локальном компьютере

Для запуска проекта необходимо иметь на установленные: node.js, python, pip.

Форкнуть репозиторий.
клонировать проект, например так:
git clone git@github.com:Temni23/foodgram-project-react.git
Вместо пути git@github.com:Temni23/foodgram-project-react.git введите свой.
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

## Альтернативная установка возможна при установленном на локальном компьютере Docker compose

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

