# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Shop Service built with Domain-Driven Design (DDD) and Clean Architecture principles using FastAPI, PostgreSQL, Redis, MongoDB, and Celery. This is a production-ready template demonstrating CQRS pattern with separated write and read models.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -e .
pip install -e ".[dev]"

# Start infrastructure services only
docker-compose up -d postgres redis mongodb

# Start all services (including API and workers)
docker-compose up -d
```

### Running the Application
```bash
# Start API server (development mode with reload)
uvicorn src.main:app --reload

# Start Celery worker (for background tasks)
celery -A src.workers.celery_app worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A src.workers.celery_app beat --loglevel=info
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_users.py

# Run specific test
pytest tests/unit/test_users.py::test_user_creation
```

### Code Quality
```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src
```

## Architecture Overview

This codebase follows **Hexagonal Architecture** (Ports & Adapters) with strict separation of concerns across four layers:

### 1. Domain Layer (`src/domain/`)
Pure business logic with zero framework dependencies. Contains:
- **Entities**: Aggregate roots (`User`, `Order`) with business rules and domain events
- **Value Objects**: Immutable objects like `Email`, `UserId`, `Money`, `OrderStatus`
- **Domain Services**: Business logic that doesn't fit in entities
- **Exceptions**: Domain-specific errors

Key principles:
- Entities emit domain events (e.g., `user_registered`, `order_confirmed`)
- Domain events are collected in `_domain_events` list and cleared after publishing
- All business invariants are enforced in the domain layer

### 2. Application Layer (`src/application/`)
Use case orchestration and application services. Contains:
- **Services**: `UserApplicationService`, `OrderApplicationService` orchestrate use cases
- **Commands**: Write operations (e.g., `CreateUserCommand`, `ConfirmOrderCommand`)
- **Queries**: Read operations (e.g., `GetUserByIdQuery`, `SearchUsersQuery`)
- **DTOs**: Data transfer objects for crossing boundaries

Key patterns:
- Services coordinate between domain entities and ports
- Commands and queries follow CQRS pattern
- DTOs convert between domain entities and external representations
- Domain events are published to messaging service after write operations

### 3. Ports Layer (`src/ports/`)
Interfaces (contracts) that define how the application interacts with external systems:
- **Base Interfaces**:
  - `BaseRepository[TEntity, TId]`: Generic base for write model repositories
  - `BaseReadModel[TId]`: Generic base for read model interfaces
- **Repository Interfaces**: `UserRepository`, `OrderRepository` for write models (extend `BaseRepository`)
- **Read Model Interfaces**: `UserReadModel`, `OrderReadModel` for read models (extend `BaseReadModel`)
- **Cache Interfaces**: `UserCache` for caching
- **External Service Interfaces**: `MessagingService`, `EmailService`

This layer defines "what" without "how" - implementations are in infrastructure layer.

#### Base Interface Pattern
The codebase uses generic base interfaces to reduce duplication:

**BaseRepository[TEntity, TId]** provides common CRUD operations:
- `get_by_id(id: TId) -> Optional[TEntity]`
- `add(entity: TEntity) -> None`
- `update(entity: TEntity) -> None`
- `delete(id: TId) -> None`

**BaseReadModel[TId]** provides common query operations:
- `get_by_id(id: TId) -> Optional[dict]`
- `create(data: dict) -> None`
- `update(id: TId, data: dict) -> None`
- `delete(id: TId) -> None`

Specific repositories inherit these and add domain-specific methods (e.g., `get_by_email` for `UserRepository`).

### 4. Infrastructure Layer (`src/infrastructure/`)
Concrete implementations of ports:
- **`db_postgres/`**: PostgreSQL implementations for write models (using SQLAlchemy)
  - Repository implementations: `PostgreSQLUserRepository`, `PostgreSQLOrderRepository`
  - SQLAlchemy models: `user_models.py`, `order_models.py`
- **`db_mongo/`**: MongoDB implementations for read models
  - Read model implementations: `MongoDBUserReadModel`, `MongoDBOrderReadModel`
- **`db_redis/`**: Redis implementations
  - Cache implementations: `RedisUserCache`
  - Messaging service: `RedisMessagingService`
- **`external/`**: External service implementations
  - Email service: `SMTPEmailService`

### 5. Interfaces Layer (`src/interfaces/`)
API layer with FastAPI routes and schemas:
- **`api/`**: REST API endpoints organized by domain
  - `users/routes.py`: User endpoints
  - `orders/routes.py`: Order endpoints
  - `health_check.py`: Health check endpoint
  - `dependencies.py`: FastAPI dependency injection setup

### 6. Workers Layer (`src/workers/`)
Background job processing with Celery:
- **`celery_app.py`**: Celery configuration and beat schedule
- **`users/tasks.py`**: User-related async tasks (e.g., welcome emails)
- **`orders/tasks.py`**: Order-related async tasks (e.g., payment processing)
- **`events/handlers.py`**: Domain event handlers
- **`scheduled/periodic_tasks.py`**: Scheduled tasks (cleanup, reports)

## Key Architectural Patterns

### CQRS (Command Query Responsibility Segregation)
- **Write Model**: PostgreSQL stores authoritative data via repositories
- **Read Model**: MongoDB optimized for queries (denormalized views)
- Application services update both models synchronously (ideally async via events)

### Domain Events
- Entities emit events when state changes (e.g., `user_registered`)
- Events are published to Redis Pub/Sub via `MessagingService`
- Celery workers subscribe to events and process them asynchronously
- Pattern: Collect events during aggregate operations, publish after save

### Dependency Injection
FastAPI's `Depends` is used for DI. See `src/interfaces/api/dependencies.py`:
- `get_user_service()`: Wires up `UserApplicationService` with all dependencies
- `get_order_service()`: Wires up `OrderApplicationService`
- Database session management via `get_db_session()`

Example usage in routes:
```python
def get_user(user_id: UUID, service: UserApplicationService = Depends(get_user_service)):
    # service is fully wired with all dependencies
```

### Repository Pattern
- All repositories extend `BaseRepository[TEntity, TId]` for common CRUD operations
- Repositories work with domain entities, not database models
- Conversion happens inside repository implementations
- Write models use repositories, read models use read model interfaces
- Domain-specific queries are added as additional methods in concrete interfaces

Example:
```python
# BaseRepository provides: get_by_id, add, update, delete
class UserRepository(BaseRepository[User, UserId]):
    # Add domain-specific method
    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        pass
```

## Configuration

All configuration is in `src/config/settings.py` using Pydantic BaseSettings:
- Environment variables loaded from `.env` file
- Database URLs constructed automatically from components
- Cache TTLs configurable per entity type

Key settings:
- `POSTGRES_URL`: Write model database
- `MONGODB_URL`: Read model database
- `REDIS_URL`: Cache and messaging
- `CELERY_BROKER_URL`: Celery task queue
- `USER_CACHE_TTL`: User cache expiration (default 3600s)

## Testing Strategy

Tests are organized under `tests/`:
- **`unit/`**: Test domain logic in isolation
- **`integration/`**: Test infrastructure adapters with real services

When writing tests:
- Mock ports (interfaces) not implementations
- Test domain entities without any infrastructure
- Use pytest fixtures in `conftest.py`

## Git Commit Conventions

This project follows Conventional Commits specification (see `.claude/conventions/git_convention.md`):

Format: `<type>[optional scope]: <description>`

Common types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Adding tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks

Examples:
```
feat(orders): add order cancellation feature
fix(users): prevent duplicate email registration
refactor(domain): extract order validation to domain service
```

## Important Implementation Notes

### Adding a New Domain Entity
1. Create entity in `src/domain/<context>/entities.py` with domain events
2. Create value objects in `value_objects.py`
3. Define repository interface in `src/ports/<context>/`:
   - Extend `BaseRepository[Entity, EntityId]` for standard CRUD
   - Add domain-specific query methods as needed
4. Implement repository in `src/infrastructure/db_postgres/`
5. Define read model interface in `src/ports/<context>/`:
   - Extend `BaseReadModel[EntityId]` for standard operations
   - Add domain-specific query methods as needed
6. Implement read model in `src/infrastructure/db_mongo/`
7. Create application service in `src/application/<context>/service.py`
8. Add FastAPI routes in `src/interfaces/api/<context>/routes.py`
9. Wire up dependencies in `src/interfaces/api/dependencies.py`

### Working with Domain Events
- Events are collected in entity's `_domain_events` list
- Call `entity.get_domain_events()` to retrieve and clear events
- Publish events via `messaging_service.publish_event()` after persisting
- Celery workers listen for events via `src/workers/events/handlers.py`

### Database Access Patterns
- Never import SQLAlchemy models in domain or application layers
- Repositories convert between domain entities and ORM models
- Use repository for writes, read models for queries
- Cache results from read models for frequently accessed data

### API Design
- All endpoints under `/api/v1` prefix
- Use Pydantic schemas in `schemas.py` for request/response validation
- Application DTOs are separate from API schemas
- Services return DTOs, routes convert to schemas