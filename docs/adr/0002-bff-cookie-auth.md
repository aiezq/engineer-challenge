# ADR 0002: Next.js BFF with httpOnly Access Token Cookie

## Status
Accepted

## Context
Нужно защитить браузерный auth-flow и при этом не скатиться в хранение токена в `localStorage`.

## Decision
Frontend обращается к backend через Next.js BFF `/api/graphql`, а access token хранится в `httpOnly` cookie.

## Rationale
- Исключает прямой доступ клиентского JS к токену.
- Позволяет server-side guard-ить приватные маршруты на уровне App Router layout.
- Сохраняет достаточно простую локальную разработку для challenge.

## Consequences
- Плюс: лучшее baseline security для browser auth.
- Плюс: проще эволюционировать в сторону refresh-token/session rotation.
- Минус: frontend становится частью auth perimeter.
