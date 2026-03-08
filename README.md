# Orbitto Auth - Advanced Engineer Challenge

Репозиторий содержит решение челленджа на позицию backend/fullstack инженера, реализованное по принципам **DDD, CQRS и IaC**. В качестве стека были выбраны **FastAPI (Python)** и **Next.js (React)**, взаимодействие между которыми построено на **GraphQL**. 

В проекте сформирована прозрачная история коммитов (12 штук), демонстрирующая последовательный подход к разработке от инициализации инфраструктуры до интеграции UI.

## Запуск проекта

**Требования:** Docker и Docker Compose (для БД и Redis), Node.js (для фронтенда), Python 3.10+ (для локального бэкенда при желании).

### Быстрый запуск с Docker Compose
```bash
# 1. Запустить инфраструктуру (PostgreSQL, Redis)
docker-compose up -d

# 2. Локальный запуск Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

# 3. Локальный запуск Frontend
cd ../frontend
npm install
npm run dev
```

После запуска:
- Frontend будет доступен по адресу: `http://localhost:3000`
- Встроенный интерфейс GraphQL (Strawberry): `http://localhost:8000/graphql`

---

## Архитектурная схема (Mermaid)

```mermaid
graph TD
    %% Frontend
    subgraph Frontend [Next.js App Router]
        UI[UI Components]
        Apollo[Apollo GraphQL Client]
        UI --> Apollo
    end

    %% Backend API
    subgraph Backend [FastAPI Application]
        GQL[GraphQL Strawberry Endpoint]
        
        %% CQRS
        subgraph AppLayer [Application Layer / CQRS]
            CMD[Command Handlers\nRegister, Login, Reset]
            QRY[Query Handlers\nGetUser, ValidateToken]
        end
        
        %% DDD
        subgraph DomainLayer [Domain Layer]
            User[User Entity]
            VO[Value Objects: Email, Password]
            Prt[Ports/Interfaces]
        end
        
        %% Infrastructure
        subgraph InfraLayer [Infrastructure Layer]
            Repo[SQLAlchemy Repository]
            Token[JWT Token Service]
            Hash[Bcrypt Hasher]
            Log[Structlog]
            Rate[Redis Rate Limiter]
            
            Repo -.-> Prt
            Token -.-> Prt
            Hash -.-> Prt
        end
        
        GQL --> CMD
        GQL --> QRY
        CMD --> DomainLayer
        CMD --> Prt
        QRY --> Prt
    end

    %% Storage
    subgraph Storage [Docker Compose IaC]
        PG[(PostgreSQL 15)]
        RD[(Redis 7)]
    end

    Apollo -- "GraphQL (HTTP)" --> GQL
    Repo --> PG
    Rate --> RD
```

---

## Как были реализованы принципы

### 1. Domain-driven Design (DDD)
- **Изоляция:** Слой `src/domain` не имеет зависимостей от фреймворков и БД.
- **Value Objects:** Введено строгую типизацию для `Email`, `RawPassword` и `HashedPassword` с проверками инвариантов на момент создания.
- **Rich User Entity:** Модель `User` инкапсулирует бизнес-правила генерации и валидации `reset_token`, запрещая внешним сервисам менять состояние напрямую: `user.request_password_reset()` и `user.reset_password()`.
- **Ports & Adapters:** Слой инфраструктуры имплементирует абстракции (порты), определенные в Application layer (`UserRepository`, `PasswordHasher`).

### 2. Command Query Responsibility Segregation (CQRS)
- **Read/Write разделение:** Логика разделена на команды (изменение состояния: регистрация, выдача токенов) и запросы (получение данных).
- **GraphQL:** Идеально ложится на эту парадигму (Mutations = Commands, Queries = Queries). 
- **ReadModels:** Запросы возвращают специально подготовленные `UserReadModel`, минуя загрузку тяжелой бизнес-сущности `User`. В реальном проекте Read репозитории могут обращаться напрямую к реплике БД или кэшу.

### 3. Infrastructure as Code (IaC)
- Инфраструктура полностью описана в `docker-compose.yml`, который поднимает PostgreSQL с healthcheck-ами и Redis для rate-limiting.

---

## Ключевые компромиссы (Trade-offs / ADRs)

1. **GraphQL вместо gRPC:** gRPC крут для микросервисов, но GraphQL предоставляет лучшую эргономику для Next.js (через Apollo) при публичном API для браузера. CQRS-команды очень легко проецировать на GraphQL Mutations.
2. **Один Read/Write репозиторий в SQLAlchemy:** Вместо создания двух независимых подключений и репозиториев для Commands и Queries (что является строгим CQRS), была применена упрощенная модель: `SqlAlchemyUserRepository` реализует оба интерфейса (`UserRepository` и `UserReadRepository`), чтобы сэкономить время в рамках челленджа.
3. **Отсутствие асинхронной шины (Event Bus):** В "чистом" DDD после `user.request_password_reset()` публикуется доменное событие (Domain Event), а хендлер отправляет письмо через RabbitMQ/Kafka. Для простоты здесь это опущено, но заложен в архитектуру.
4. **Хранение токенов Next.js:** Выбрано сохранение в `localStorage` (через Apollo middleware) для симуляции реального приложения. На проде лучше использовать `httpOnly Cookies`, чтобы избежать XSS-рисков.

---

## Следующие шаги для Production-версии

- [ ] **IaC Evolution:** Переписать развёртывание на Terraform + Helm Charts для Kubernetes (ingress, cert-manager).
- [ ] **Безопасность UI:** Перевести аутентификацию на HttpOnly Secure Cookies через Backend-For-Frontend (BFF) или Next.js Route Handlers.
- [ ] **Event-Driven Broker:** Внедрить RabbitMQ / Kafka или хотя бы Celery/Redis Queue для обработки Domain Events (рассылка писем, аналитика регистраций).
- [ ] **Миграции БД:** Добавить Alembic для контроля версионирования схемы БД.
- [ ] **Outbox Pattern:** Добавить паттерн Transactional Outbox для синхронизации транзакций БД с публикацией событий.
