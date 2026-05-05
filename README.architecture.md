# Architecture Documentation - Lidercom KR Peru Platform

## Table of Contents
- [Architectural Overview](#architectural-overview)
- [Design Patterns](#design-patterns)
- [Module Architecture](#module-architecture)
- [Data Flow Diagrams](#data-flow-diagrams)
- [Technology Integration](#technology-integration)
- [Decision Records](#decision-records)

---

## Architectural Overview

### Hexagonal Architecture (Ports & Adapters)

```
                    ┌─────────────────────────┐
                    │      GraphQL API        │
                    │   (Driving Adapter)     │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    Driving Ports        │
                    │  (Input Interfaces)     │
                    └───────────┬─────────────┘
                                │
┌───────────────────────────────────────────────────────┐
│                  DOMAIN LAYER                          │
│  ┌─────────────┐          ┌──────────────────────┐   │
│  │  ENTITIES   │◄────────►│      SERVICES       │   │
│  │ (Business   │          │   (Business Logic)   │   │
│  │  Objects)   │          │                      │   │
│  └─────────────┘          └──────────────────────┘   │
└───────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    Driven Ports        │
                    │  (Output Interfaces)   │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌─────────▼────────┐    ┌───────▼────────┐
│  Redis Adapter │    │  Celery Adapter  │    │  Rust Adapter  │
│  (Driven)      │    │  (Driven)        │    │  (Driven)      │
└────────────────┘    └──────────────────┘    └────────────────┘
```

### Screaming Architecture

Top-level directories express **business capabilities**, not technical layers:

| Directory | Business Capability |
|-----------|-------------------|
| `auth/` | User authentication & transaction validation |
| `ml/` | Machine learning predictions & training |
| `wallet/` | Blockchain wallet operations |
| `graphql/` | API layer configuration |
| `db/` | Persistence management |
| `k8s/` | Infrastructure orchestration |
| `shared/` | Cross-cutting concerns |

---

## Design Patterns

### 1. Dependency Inversion Principle (DIP)
Domain layer defines interfaces (ports). Adapters implement them.

```python
# Domain Port (auth/ports/driven/user_repository.py)
class UserRepositoryPort(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

# Adapter Implementation (auth/adapters/driven/postgres_user_repo.py)
class PostgresUserRepository(UserRepositoryPort):
    def find_by_email(self, email: str) -> Optional[User]:
        # PostgreSQL implementation
        pass
```

### 2. Ports Classification

**Driving Ports (Input)**: How external world triggers the domain
- GraphQL resolvers
- API endpoints
- Message queue consumers

**Driven Ports (Output)**: How domain accesses external services
- Database repositories
- External API clients
- Message queue publishers
- Cache clients

### 3. Domain Model Isolation
The domain layer has **zero dependencies** on external frameworks or libraries.

---

## Module Architecture

### `auth/` - Authentication Module

```
auth/
├── domain/
│   ├── entities/
│   │   ├── user.py           # User aggregate root
│   │   ├── session.py        # Auth session entity
│   │   └── auth_transaction.py  # Transaction validation entity
│   └── services/
│       ├── login_service.py  # Login business logic
│       ├── token_service.py  # JWT/token generation
│       └── transaction_validator.py  # Transaction validation rules
├── ports/
│   ├── driving/
│   │   └── auth_input_port.py    # Interface for auth triggers
│   └── driven/
│       ├── user_repository_port.py    # Interface for user data access
│       └── token_storage_port.py     # Interface for token persistence
└── adapters/
    ├── driving/graphql/
    │   └── auth_resolver.py    # GraphQL resolver implementation
    └── driven/
        ├── postgres_user_repo.py   # PostgreSQL implementation
        └── redis_token_storage.py  # Redis token storage
```

**Flow**: GraphQL Request → Driving Port → Domain Service → Driven Port → Adapter (DB/Redis)

---

### `ml/` - Machine Learning Module

```
ml/
├── domain/
│   ├── entities/
│   │   ├── ml_model.py        # ML model entity
│   │   ├── prediction_job.py  # Async prediction job
│   │   └── training_data.py   # Training dataset entity
│   └── services/
│       ├── prediction_service.py  # Orchestrates predictions
│       └── job_scheduler.py       # ML job scheduling logic
├── ports/
│   ├── driving/
│   │   └── ml_input_port.py       # Trigger predictions
│   └── driven/
│       ├── cache_port.py          # Caching interface
│       └── task_queue_port.py     # Async task interface
└── adapters/
    ├── driving/graphql/
    │   └── ml_resolver.py         # GraphQL endpoints
    └── driven/
        ├── redis_cache.py         # Redis caching
        └── celery_worker.py       # Celery task execution
```

**Redis Usage**: Model result caching, session storage, feature caching
**Celery Usage**: Async ML job execution, training pipelines, batch predictions

---

### `wallet/` - Blockchain Wallet Module

```
wallet/
├── domain/
│   ├── entities/
│   │   ├── wallet.py          # Wallet aggregate root
│   │   ├── transaction.py     # Blockchain transaction
│   │   └── address.py         # Blockchain address
│   └── services/
│       ├── wallet_service.py  # Core wallet operations
│       ├── transaction_validator.py  # Tx validation logic
│       └── rust_core_client.py       # Rust core integration
├── ports/
│   ├── driving/
│   │   └── wallet_input_port.py     # Wallet operation triggers
│   └── driven/
│       ├── rust_core_port.py        # Rust core interface
│       └── blockchain_node_port.py   # Blockchain node interface
├── adapters/
│   ├── driving/graphql/
│   │   └── wallet_resolver.py       # GraphQL wallet API
│   └── driven/
│       ├── rust_ffi.py              # Rust FFI binding
│       └── blockchain_rpc.py        # Blockchain JSON-RPC client
└── rust/
    ├── src/
    │   ├── lib.rs                    # Rust core library
    │   ├── wallet_core.rs            # Wallet logic in Rust
    │   └── crypto_ops.rs             # Cryptographic operations
    ├── Cargo.toml
    └── build.rs
```

**Rust Integration**: Core wallet logic (crypto, signing) implemented in Rust for safety/performance
**Blockchain**: Interacts with blockchain nodes via RPC/WebSocket

---

## Data Flow Diagrams

### Authentication Flow with Transaction Validation

```
[Client] --GraphQL--> [AuthResolver] --driving port--> [LoginService]
                                                        |
                                              [TransactionValidator]
                                                        |
                                    ┌───────────────────┼───────────────────┐
                                    │                   │                   │
                            [UserRepository]    [TokenStorage]    [TransactionRepo]
                              (PostgreSQL)        (Redis)         (PostgreSQL)
```

### ML Prediction Flow

```
[Client] --GraphQL--> [MLResolver] --driving port--> [PredictionService]
                                                        |
                                              [JobScheduler]
                                                        |
                                    ┌───────────────────┴───────────────────┐
                                    │                                       │
                              [RedisCache]                            [CeleryWorker]
                            (Check cached result)                  (Execute ML model)
                                                                        │
                                                                [MLModel Entity]
                                                                        │
                                                              [Store in Redis]
```

### Wallet Operation Flow

```
[Client] --GraphQL--> [WalletResolver] --driving port--> [WalletService]
                                                              │
                                                    [TransactionValidator]
                                                              │
                                        ┌─────────────────────┼─────────────────────┐
                                        │                     │                     │
                                  [RustCore]           [BlockchainNode]      [WalletRepo]
                               (Crypto operations)     (Broadcast tx)       (PostgreSQL)
```

---

## Technology Integration

### GraphQL Layer
- **Purpose**: Unified API entry point for all modules
- **Location**: `graphql/` (shared schema) + `*/adapters/driving/graphql/`
- **Tools**: Strawberry (Python), Apollo Server, or similar

### Redis (ML Module)
| Use Case | Implementation |
|----------|----------------|
| Model caching | Cache prediction results with TTL |
| Session storage | Store ML job sessions |
| Feature cache | Cache preprocessed features |
| Pub/Sub | Celery task signaling |

### Celery (ML Module)
| Use Case | Implementation |
|----------|----------------|
| Async predictions | Background ML inference tasks |
| Model training | Scheduled training pipelines |
| Batch processing | Bulk prediction jobs |
| Task chaining | Multi-step ML workflows |

### Rust (Wallet Module)
| Use Case | Implementation |
|----------|----------------|
| Crypto operations | Key generation, signing, verification |
| Memory safety | Prevents common crypto vulnerabilities |
| FFI | Python-Rust bindings via PyO3 or cffi |
| Performance | Critical path operations in compiled code |

### Blockchain Integration (Wallet Module)
- **Node Communication**: JSON-RPC / WebSocket to blockchain nodes
- **Transaction Broadcasting**: Submit signed transactions to network
- **Balance Queries**: Read on-chain state
- **Event Listening**: Subscribe to wallet-related on-chain events

---

## Decision Records

### ADR 001: Hexagonal Architecture Choice
**Status**: Accepted
**Context**: Need to isolate business logic from infrastructure changes
**Decision**: Use hexagonal architecture with ports & adapters
**Consequences**:
- ✅ Easy to swap adapters (e.g., PostgreSQL → MongoDB)
- ✅ Domain logic is framework-agnostic and testable
- ⚠️ More boilerplate code for ports/interfaces

### ADR 002: Screaming Architecture for Top-Level Structure
**Status**: Accepted
**Context**: Need clear business intent in project structure
**Decision**: Top-level folders represent business capabilities
**Consequences**:
- ✅ New developers understand business domain immediately
- ✅ Aligns with Domain-Driven Design (DDD)
- ✅ Easy to identify bounded contexts

### ADR 003: Rust for Wallet Core Logic
**Status**: Accepted
**Context**: Wallet crypto operations need memory safety and performance
**Decision**: Implement core wallet logic in Rust, integrate via FFI
**Consequences**:
- ✅ Memory-safe cryptographic operations
- ✅ High performance for critical operations
- ⚠️ Additional build complexity (Rust toolchain)
- ⚠️ FFI integration overhead

### ADR 004: Celery + Redis for ML Operations
**Status**: Accepted
**Context**: ML predictions can be time-consuming and need async execution
**Decision**: Use Celery for task queue, Redis for results caching
**Consequences**:
- ✅ Non-blocking ML predictions via async tasks
- ✅ Horizontal scaling of workers
- ✅ Result caching reduces redundant computations
- ⚠️ Additional infrastructure components to manage

### ADR 005: GraphQL as Single API Layer
**Status**: Accepted
**Context**: Need flexible API that serves multiple client types
**Decision**: Use GraphQL as unified API entry point
**Consequences**:
- ✅ Clients request exactly the data they need
- ✅ Single endpoint for all modules
- ✅ Strong typing with schema
- ⚠️ Learning curve for REST-focused developers

---

## Testing Strategy

### Domain Layer
- Pure unit tests (no mocks needed for business logic)
- Test entities, value objects, and domain services in isolation

### Port Interfaces
- Define test contracts that all adapters must satisfy
- Use ports to inject mocks in driving adapter tests

### Adapter Layer
- Integration tests with real infrastructure (Redis, PostgreSQL, etc.)
- Use test containers for database/Redis tests
- Mock external services (blockchain nodes) in adapter tests

### End-to-End
- GraphQL endpoint tests with test client
- Full flow: GraphQL → Domain → Adapter → Infrastructure

---

## Build & Deployment

### Local Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Rust (for wallet module)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build Rust library
cd wallet/rust && cargo build --release

# Start Redis
docker run -d -p 6379:6379 redis

# Start Celery worker
celery -A ml.adapters.driven.celery_app worker --loglevel=info

# Run GraphQL server
uvicorn graphql.server:app --reload
```

### Kubernetes Deployment
```bash
# Apply all K8s manifests
kubectl apply -f k8s/

# Deployments include:
# - GraphQL API server
# - Celery workers (ML)
# - Redis instance
# - PostgreSQL database
# - Rust core service (if applicable)
```

---

## Module Dependency Graph

```
shared/ (errors, utils, config)
    ↑
    ├── auth/ ────────┐
    │                 │
    ├── ml/ ──────────┼──► graphql/ (schema)
    │                 │
    ├── wallet/ ──────┘
         │
         └──► wallet/rust/ (compiled dependency)
```

All modules depend on `shared/`. Modules do not depend on each other directly (loose coupling via events or shared kernel if needed).

---

*Last updated: 2026-05-05*
