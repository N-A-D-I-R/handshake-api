# GoBarter Backend

Это бэкенд для проекта **GoBarter** — платформы для обмена товарами и услугами. Реализован с использованием **FastAPI**, **SQLAlchemy**, **Alembic** и других современных инструментов Python.

---

## 📦 Установка зависимостей

```bash
pip install -r requirements.txt
```

## 🗄️ Работа с миграциями

### Обновление базы данных до последней миграции:

```bash
alembic upgrade head
```

### Создание новой миграции:

```bash
alembic revision --autogenerate -m "описание миграции"
```

## 🚀 Запуск приложения

```bash
uvicorn main:app --reload
```

> Параметр `--reload` автоматически перезапускает сервер при изменении исходного кода