# twa-sub-pro

> **NDA**: Исходный код в этом репозитории является витринной версией. Полная реализация, бизнес-логика и конфигурации, специфичные для заказчика, являются проприетарными и охраняются соглашением о неразглашении.

Полнофункциональный MVP-шаблон сервиса подписок для Telegram Mini Apps. Проект демонстрирует интеграцию FastAPI с Telegram Web Apps API и организацию асинхронной работы с базой данных.

---

## Стек технологий

| Слой | Технология |
|---|---|
| Язык | Python 3.10+ |
| API-фреймворк | FastAPI 0.104 |
| ORM | SQLAlchemy 2.0 (async) |
| База данных | SQLite (через aiosqlite) |
| Валидация | Pydantic v2 |
| Настройки | pydantic-settings |
| Фронтенд | HTML5, CSS3, Vanilla JavaScript |
| Интеграция с Telegram | Telegram Web App JS API |
| Сервер | Uvicorn |

---

## Структура проекта

```
miniapp/
├── app/
│   ├── routes/
│   │   ├── auth.py             # /api/auth — верификация и поиск пользователей
│   │   └── subscriptions.py    # /api/subscriptions — планы и покупки
│   ├── auth_utils.py           # Парсер Telegram initData
│   ├── config.py               # Настройки через pydantic-settings (.env)
│   ├── database.py             # Async-движок и сессия SQLAlchemy
│   ├── dependencies.py         # Dependency injection FastAPI (get_db)
│   ├── models.py               # ORM-модели: User, Plan, Subscription
│   └── schemas.py              # Pydantic-схемы запросов и ответов
├── static/
│   ├── index.html              # SPA-интерфейс Telegram Mini App
│   ├── app.js                  # Логика фронтенда, вызовы Telegram WebApp API
│   └── styles.css              # Стили приложения
├── main.py                     # Точка входа FastAPI-приложения
├── init_db.py                  # Инициализация и наполнение БД (планы Basic/Pro/Premium)
├── requirements.txt
└── .env.example
```

---

## Ключевые возможности

- **Парсинг Telegram initData** — серверный парсинг `initData`, передаваемого Telegram-клиентом, с готовой заглушкой HMAC-SHA256 валидации для активации в продакшне.
- **Динамический интерфейс в зависимости от статуса подписки** — фронтенд отображает разные разделы в зависимости от того, верифицирован ли пользователь и есть ли у него активная подписка.
- **Интеграция с Telegram MainButton** — использует нативный компонент `MainButton` Telegram для управления процессом покупки подписки.
- **Полностью асинхронный слой БД** — все операции с базой данных используют async-сессии SQLAlchemy 2.0 на основе `aiosqlite`; блокирующих вызовов в обработчиках запросов нет.
- **Управление планами подписок** — в БД заданы три плана (Basic, Pro, Premium); планы загружаются динамически из базы данных.
- **Mock-платежный поток** — эндпоинт покупки имитирует оплату и активирует премиум-статус пользователя, что позволяет легко подключить реального платежного провайдера.
- **Автоматическое создание таблиц при запуске** — `Base.metadata.create_all` выполняется при старте приложения через lifecycle-событие FastAPI; инструменты миграции для локальной разработки не требуются.
- **Эндпоинт проверки здоровья** — `GET /health` возвращает `{"status": "ok"}` для простых проверок работоспособности.

---

## Установка и запуск

### 1. Создание виртуального окружения и установка зависимостей

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Настройка окружения

Скопируйте файл примера и заполните необходимые значения:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Отредактируйте `.env`:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | Токен вашего Telegram-бота от @BotFather (обязательно) |
| `SECRET_KEY` | `your-secret-key-change-in-production` | Секрет для внутренней подписи |
| `DATABASE_URL` | `sqlite+aiosqlite:///./app.db` | URL базы данных SQLAlchemy |
| `DEBUG` | `True` | Флаг режима отладки |

### 3. Инициализация базы данных

```bash
python init_db.py
```

Создает все таблицы и наполняет базу тремя планами подписок: Basic, Pro и Premium.

### 4. Запуск сервера

```bash
python main.py
```

Приложение будет доступно по адресу `http://localhost:8000`.

Для подключения приложения к Telegram-клиенту во время локальной разработки используйте инструмент туннелирования, например ngrok:

```bash
ngrok http 8000
```

Укажите полученный HTTPS-URL в качестве Web App URL бота через @BotFather.

---

## API-эндпоинты

### Аутентификация

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/auth/verify` | Парсинг и верификация пользователя через Telegram `initData` |
| `GET` | `/api/auth/user/{telegram_id}` | Получение информации о пользователе по Telegram ID |

### Управление подписками

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/subscriptions/plans` | Список всех доступных планов подписок |
| `GET` | `/api/subscriptions/plans/{plan_id}` | Получение конкретного плана по ID |
| `POST` | `/api/subscriptions/purchase` | Обработка покупки подписки |
| `GET` | `/api/subscriptions/user/{user_id}` | Все подписки пользователя |
| `GET` | `/api/subscriptions/active/{user_id}` | Только активные подписки пользователя |

---

## Модели базы данных

| Модель | Таблица | Описание |
|---|---|---|
| `User` | `users` | Пользователь Telegram: `telegram_id`, `username`, `first_name`, `is_premium` |
| `Plan` | `plans` | План подписки: `name`, `price`, `duration_days`, `features` |
| `Subscription` | `subscriptions` | Запись подписки: `plan_name`, `price`, `expires_at`, `is_active` |

---

## Безопасность

- Функция `verify_telegram_init_data` в `app/auth_utils.py` находится в режиме **локального тестирования** — она парсит `initData`, но не выполняет полную криптографическую проверку подписи HMAC-SHA256. Перед развертыванием в продакшне необходимо активировать полную валидацию подписи с использованием `TELEGRAM_BOT_TOKEN` в качестве HMAC-ключа.
- Никогда не коммитьте файл `.env` в систему контроля версий. Добавьте его в `.gitignore`.
- Файл `app.db` с данными пользователей также должен быть исключен из системы контроля версий. Каждый разработчик создает свою локальную копию базы данных командой `python init_db.py`.

---

## Лицензия

MIT
