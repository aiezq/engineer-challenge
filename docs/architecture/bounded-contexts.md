# Bounded Contexts

## Authentication Context
Основной bounded context этого челленджа.

Язык предметной области:
- `User`
- `Email`
- `RawPassword`
- `HashedPassword`
- `Reset Token`
- `Authenticate`
- `Register`
- `Request Password Reset`
- `Reset Password`

Основные инварианты:
- e-mail нормализуется (`trim + lowercase`) и проходит доменную валидацию
- пароль не хранится в открытом виде
- reset token хранится только в виде hash
- reset token имеет срок жизни и инвалидируется после успешного использования
- auth/reset endpoint-ы ограничены rate limiting

Границы:
- `src/domain` описывает сущности и value objects
- `src/application/commands` описывает mutation/command side
- `src/application/queries` описывает read/query side
- `src/infrastructure` содержит adapters к БД, Redis, JWT, bcrypt и logging

## Web/BFF Context
Supporting context на стороне frontend.

Ответственность:
- UI по дизайн-макету
- хранение access token в `httpOnly` cookie
- проксирование GraphQL-запросов через Next.js route handler
- server-side guard приватных роутов

Этот контекст сознательно не смешивает бизнес-правила аутентификации с UI-слоем и не дублирует доменную логику backend.
