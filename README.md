## Автотесты для сервиса публикации новостей ya_news и сервиса публикации заметок ya_notes.

### Технологии:
* Python 3.11
* Django 3.2.16
* pytest 7.1.3
* pytest-django 4.5.2
* unittest

### Запуск проекта
Клонировать проект c GitHub:
```
git clone git@github.com:chrnmaxim/django_testing.git
```
Установить виртуальное окружение:
```
python -m venv venv
```
Активировать виртуальное окружениe:
```
. venv/Scripts/activate
```
Обновить менеджер пакетов pip:
```
python -m pip install --upgrade pip
```
Установить зависимости из requirements.txt:
```
pip install -r requirements.txt
``` 
Для запуска тестов сервиса публикации новостей ya_new перейдите в директорию **ya_news/** и выполните команду
```
pytest
``` 
Для запуска тестов сервиса публикации заметок ya_notes перейдите в директорию **ya_note/** и выполните команду
```
python manage.py test
```
