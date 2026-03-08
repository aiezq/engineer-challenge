# ADR 0001: GraphQL as Primary Client Transport

## Status
Accepted

## Context
Челлендж допускает `gRPC` и/или `GraphQL`, при этом клиентская часть уже имеет выраженный UI-слой и несколько auth-сценариев, которые удобно описываются mutation/query контрактами.

## Decision
Основной внешний контракт реализован через GraphQL на Strawberry/FastAPI.

## Rationale
- Auth use cases естественно выражаются через `mutations` и `queries`.
- Next.js + Apollo дают минимальное трение для клиентской части.
- CQRS-подход прозрачно проецируется на GraphQL: mutation = command, query = query side.
- Для challenge-формата GraphQL дает лучшую демонстрацию доменной модели, чем шаблонный REST.

## Consequences
- Плюс: richer contract для frontend и наглядное read/write разделение.
- Минус: меньше строгости transport-schema, чем у protobuf/gRPC.
- Минус: для межсервисного окружения production-эволюции можно рассмотреть dual-stack с internal gRPC и public GraphQL/BFF.
