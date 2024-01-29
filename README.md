# Решение на тестовое задание от компании Tripster.

## ТЗ:

## Реализовать API на Django или FastAPI:
- Добавление публикации (на вход — текст публикации)
- Просмотр списка из 10 публикаций последних | самых рейтинговых
- Голосование за публикацию (+/- или отмена голоса)
## Правила и ограничения:
- Создавать публикацию и голосовать могут только авторизованные пользователи
- Один пользователь не может проголосовать за одну публикацию дважды. Переголосовать или отозвать голос можно
- Рейтинг публикации считается как число плюсов - число минусов
## Данные о публикации должны содержать следующие данные:
- Текст публикации
- Дата публикации
- Автор
- Число голосов
## Рейтинг
- Сервис должен выдерживать нагрузку и обрабатывать ситуации с параллельными запросами на создание публикации, голосование и т.п.

# Запуск
- Запускаем в корневой папке проект:
`docker-compose -f .\docker-compose.yml up -d`
- Создаем миграции
`docker-compose exec app makemigrations *migration_name*`
- Прогнать миграции
`docker compose exec app migrate`
- Сервер будет доступен под URL-адресу `http://localhost:16000/`
- Swagger будет доступен по `http://localhost:16000/docs#/` | `http://localhost:16000/redocs#/`
# Стэк
- Python 3.12
- FastAPI ~=0.109.0
- Postgres 14.1
