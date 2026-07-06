# Employee Registry API

Тестовый проект — реестр сотрудников с веб-интерфейсом.

## Стек

- Python 3.13
- FastAPI — веб-фреймворк
- SQLAlchemy — ORM
- PostgreSQL — база данных
- Alembic — миграции
- Jinja2 + Tailwind CSS — шаблоны
- Docker Compose — запуск

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/employees/` | Список сотрудников (с фильтрацией и пагинацией) |
| GET | `/employees/create` | Форма добавления сотрудника |
| POST | `/employees/create` | Создать сотрудника |
| GET | `/employees/{employee_id}/edit` | Форма редактирования |
| POST | `/employees/{employee_id}` | Обновить сотрудника |
| POST | `/employees/{employee_id}/delete` | Удалить сотрудника |
| GET | `/health` | Проверка работоспособности |

## Фильтрация

При работе со списком сотрудников доступны следующие фильтры:

- Поиск по ФИО (одно или несколько слов)
- Поиск по телефону (10 цифр после +7)
- Фильтр по полу (мужской / женский)
- Фильтр по возрасту (от / до)

## Структура проекта

```
employee-registry-api/
├── src/
│   └── app/
│       ├── core/          # Конфигурация
│       ├── dependencies/  # Dependency injection
│       ├── models/        # SQLAlchemy модели
│       ├── repositories/  # Работа с БД
│       ├── routers/       # API и веб-роуты
│       ├── schemas/       # Pydantic схемы
│       ├── services/      # Бизнес-логика
│       ├── templates/     # Jinja2 шаблоны
│       ├── uploads/       # Загруженные фото
│       ├── utils/         # Утилиты
│       └── main.py        # Точка входа
├── alembic/               # Миграции
├── .env.example           # Пример переменных окружения
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Лицензия

MIT
