# twa-sub-pro

A full-featured MVP template for a Telegram Mini App subscription service. The project demonstrates FastAPI integration with the Telegram Web Apps API and the organization of async database operations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| API Framework | FastAPI 0.104 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite (via aiosqlite) |
| Validation | Pydantic v2 |
| Settings | pydantic-settings |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Telegram Integration | Telegram Web App JS API |
| Server | Uvicorn |

---

## Project Structure

```
miniapp/
├── app/
│   ├── routes/
│   │   ├── auth.py             # /api/auth — user verification & lookup
│   │   └── subscriptions.py    # /api/subscriptions — plans & purchases
│   ├── auth_utils.py           # Telegram initData parser
│   ├── config.py               # Settings via pydantic-settings (.env)
│   ├── database.py             # SQLAlchemy async engine & session
│   ├── dependencies.py         # FastAPI dependency injection (get_db)
│   ├── models.py               # ORM models: User, Plan, Subscription
│   └── schemas.py              # Pydantic request/response schemas
├── static/
│   ├── index.html              # Single-page Telegram Mini App UI
│   ├── app.js                  # Frontend logic, Telegram WebApp API calls
│   └── styles.css              # Application styles
├── main.py                     # FastAPI application entry point
├── init_db.py                  # DB initialization & seed (Basic/Pro/Premium plans)
├── requirements.txt
└── .env.example
```

---

## Key Features

- **Telegram initData parsing** — server-side parsing of `initData` passed by the Telegram client, with a HMAC-SHA256 validation stub ready for production activation.
- **Dynamic UI based on subscription status** — the frontend shows different sections depending on whether the user is verified and whether they hold an active subscription.
- **Telegram MainButton integration** — uses the native Telegram `MainButton` component to drive the subscription purchase flow.
- **Fully async database layer** — all database operations use SQLAlchemy 2.0 async sessions backed by `aiosqlite`; no blocking calls in request handlers.
- **Subscription plan management** — seeded with three plans (Basic, Pro, Premium); plans are fetched dynamically from the database.
- **Mock payment flow** — purchase endpoint simulates a payment and activates the user's premium status, making it easy to replace with a real payment provider.
- **Auto table creation on startup** — `Base.metadata.create_all` runs on application startup via a FastAPI lifecycle event; no migration tooling required for local development.
- **Health endpoint** — `GET /health` returns `{"status": "ok"}` for simple liveness checks.

---

## Installation & Setup

### 1. Create virtual environment and install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

Copy the example file and fill in the required values:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Edit `.env`:

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | Your Telegram Bot token from @BotFather (required) |
| `SECRET_KEY` | `your-secret-key-change-in-production` | Secret used for internal signing |
| `DATABASE_URL` | `sqlite+aiosqlite:///./app.db` | SQLAlchemy database URL |
| `DEBUG` | `True` | Debug mode flag |

### 3. Initialize the database

```bash
python init_db.py
```

This creates all tables and seeds three subscription plans: Basic, Pro, and Premium.

### 4. Start the server

```bash
python main.py
```

The application will be available at `http://localhost:8000`.

To expose the app to the Telegram client during local development, use a tunneling tool such as ngrok:

```bash
ngrok http 8000
```

Set the resulting HTTPS URL as your bot's Web App URL via @BotFather.

---

## API Endpoints

### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/verify` | Parse and verify user via Telegram `initData` |
| `GET` | `/api/auth/user/{telegram_id}` | Get user information by Telegram ID |

### Subscription Management

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/subscriptions/plans` | List all available subscription plans |
| `GET` | `/api/subscriptions/plans/{plan_id}` | Get a specific plan by ID |
| `POST` | `/api/subscriptions/purchase` | Process a subscription purchase |
| `GET` | `/api/subscriptions/user/{user_id}` | Get all subscriptions for a user |
| `GET` | `/api/subscriptions/active/{user_id}` | Get only active subscriptions for a user |

---

## Database Models

| Model | Table | Description |
|---|---|---|
| `User` | `users` | Telegram user: `telegram_id`, `username`, `first_name`, `is_premium` |
| `Plan` | `plans` | Subscription plan: `name`, `price`, `duration_days`, `features` |
| `Subscription` | `subscriptions` | User subscription record: `plan_name`, `price`, `expires_at`, `is_active` |

---

## Security Notes

- The `verify_telegram_init_data` function in `app/auth_utils.py` is currently set to **local testing mode** — it parses `initData` but does not perform the full HMAC-SHA256 cryptographic signature check. Before deploying to production, activate the complete signature validation using `TELEGRAM_BOT_TOKEN` as the HMAC key.
- Never commit the `.env` file to version control. Add it to `.gitignore`.
- The `app.db` SQLite file contains user data and should also be excluded from version control. Each developer generates their own local copy via `python init_db.py`.

---

## License

MIT
