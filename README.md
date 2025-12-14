# Shop Service - DDD + FastAPI Application

A production-ready Shop Service built with **Domain-Driven Design (DDD)** and **Clean Architecture** principles. It leverages **FastAPI**, **PostgreSQL**, **MongoDB**, **Redis**, and **Celery** to demonstrate a scalable and maintainable microservice architecture.

## 🏗 Architecture

This project strictly follows **Hexagonal Architecture (Ports & Adapters)** and **DDD** strategic patterns to decouple business logic from infrastructure and frameworks.

### Layers

- **Domain Layer** (`src/domain`): The heart of the software. Contains entities, value objects, domain exceptions, and domain services. It has **zero dependencies** on outer layers.
- **Application Layer** (`src/application`): Orchestrates use cases (Commands and Queries). It implements the specific business rules of the application, coordinating between the domain and infrastructure via ports.
- **Ports Layer** (`src/ports`): Defines the contracts (interfaces) that the infrastructure layer must implement. This ensures the Inversion of Control (IoC).
- **Infrastructure Layer** (`src/infrastructure`): Provides concrete implementations of the ports. This is where databases, external APIs, and caches are accessed.
- **Interfaces Layer** (`src/interfaces`): The entry points to the application (e.g., REST API routes using FastAPI).
- **Workers Layer** (`src/workers`): Handles background tasks and event processing using Celery.

### Key Patterns

- **CQRS (Command Query Responsibility Segregation)**: 
  - **Writes (Commands)** are handled by PostgreSQL to ensure ACID compliance.
  - **Reads (Queries)** are handled by MongoDB (denormalized read models) for high-performance retrieval.
- **Event-Driven Architecture**: Domain events are published to trigger side effects (e.g., sending emails, updating read models) asynchronously.
- **Repository Pattern**: Abstraction over data persistence.
- **Unit of Work**: Ensures atomicity for business transactions.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) v2
- **Database (Write)**: PostgreSQL (accessed via SQLAlchemy 2.0)
- **Database (Read)**: MongoDB (accessed via PyMongo)
- **Cache & Broker**: Redis
- **Background Tasks**: Celery
- **Migrations**: Alembic (implied)
- **Testing**: Pytest, Pytest-Cov
- **Linting & Formatting**: Ruff, Black, Mypy

## 📂 Project Structure

```text
shop_service/
├── .github/                   # GitHub Actions (CI/CD)
├── .venv/                     # Virtual environment
├── src/                       # Source code
│   ├── application/           # Application Logic (Use Cases)
│   │   ├── orders/            # Order Use Cases
│   │   └── users/             # User Use Cases
│   ├── config/                # Configuration & Settings
│   ├── domain/                # Enterprise Business Logic
│   │   ├── orders/            # Order Aggregates, Entities
│   │   └── users/             # User Aggregates, Entities
│   ├── infrastructure/        # Frameworks & Drivers
│   │   ├── db_mongo/          # MongoDB implementations
│   │   ├── db_postgres/       # PostgreSQL implementations
│   │   ├── db_redis/          # Redis implementations
│   │   ├── external/          # 3rd party service adapters
│   │   └── migrations/        # Database migrations
│   ├── interfaces/            # Interface Adapters
│   │   └── api/               # REST API (FastAPI routes)
│   ├── ports/                 # Input/Output Ports (Interfaces)
│   ├── shared/                # Shared Kernel / Utilities
│   └── workers/               # Background Workers (Celery)
├── tests/                     # Test Suite
│   ├── integration/           # Integration Tests
│   └── unit/                  # Unit Tests
├── docker-compose.yml         # Local development services
├── Dockerfile                 # Application container definition
├── pyproject.toml             # Python dependencies & tool config
└── README.md                  # This file
```

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10 or higher
- Docker & Docker Compose
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd python-ddd-template
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Environment Configuration**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   *Note: Ensure `.env` contains valid credentials for your local setup.*

5. **Start Infrastructure Services**
   Use Docker Compose to start PostgreSQL, MongoDB, and Redis:
   ```bash
   docker-compose up -d postgres redis mongodb
   ```

6. **Run the Application**
   ```bash
   uvicorn src.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

7. **Start Celery Worker (Optional)**
   For processing background tasks:
   ```bash
   celery -A src.workers.celery_app worker --loglevel=info
   ```

## ⚙️ Configuration

The application is configured via environment variables (loaded from `.env`). Key settings include:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Name of the service | Shop Service |
| `POSTGRES_HOST` | PostgreSQL Host | localhost |
| `POSTGRES_DB` | PostgreSQL Database Name | shop_db |
| `MONGODB_HOST` | MongoDB Host | localhost |
| `REDIS_HOST` | Redis Host | localhost |
| `CELERY_BROKER_URL` | Broker URL | redis://localhost:6379/1 |

See `src/config/settings.py` for the complete list of available configurations.

## 🧪 Testing

The project uses `pytest` for testing. Tests are split into unit (fast, isolated) and integration (slow, real dependencies) tests.

**Run all tests:**
```bash
pytest
```

**Run with coverage report:**
```bash
pytest --cov=src --cov-report=html
```

## 💻 Code Quality

We use modern Python tooling to ensure code quality:

- **Format**: `black src tests`
- **Lint**: `ruff check src tests`
- **Type Check**: `mypy src`

## ✨ Features

- **User Management**: Registration, CRUD, Search (Read Model).
- **Order Management**: Complex domain logic for ordering, adding items, confirmation.
- **Asynchronous Processing**:
  - Welcome emails.
  - Order confirmation processing.
  - Read model synchronization (Projection).
- **Resiliency**: Retry mechanisms for external services.

## 🤝 Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.