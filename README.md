# Lidercom KR-Peru Platform — ML Backend

Backend platform for **Lidercom (MW Coach inc)** managing educational/training workshops in Peru and Korea. Integrates **GraphQL APIs**, **blockchain-based identity wallets** (Substrate/JAM), and **ML processing pipelines**.

## Features

- **Workshop Management** — programs, teams, participants, observations, and metrics
- **GraphQL API** — single unified API layer via Strawberry GraphQL
- **Blockchain Identity** — sr25519 wallet generation, JAM payload signing, role-based on-chain visibility
- **Cryptography** — Argon2 key derivation, AES-256-GCM encryption for sensitive data
- **ML Processing** (planned) — Redis + Celery for async ML job execution
- **Hexagonal Architecture** — Ports & Adapters with Screaming Architecture for maintainability

## Tech Stack

| Layer | Technology |
|---|---|
| API | Strawberry GraphQL (FastAPI/ASGI) |
| Language | Python 3.13+, Rust 2024 edition |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL (TimescaleDB planned) |
| Migrations | Alembic |
| Blockchain | Substrate (`sp-core`), sr25519, JAM |
| Crypto | Argon2, AES-256-GCM |
| Queue (planned) | Redis + Celery |
| Deployment | Docker, Kubernetes (planned) |

## Architecture

The project follows **Hexagonal (Ports & Adapters) Architecture** with **Screaming Architecture** — modules are organized by business capability (`auth/`, `ml/`, `wallet/`, `graphql/`, `db/`), not by technical layer.

```
App/
├── auth/          # Authentication module
│   ├── domain/    # Entities, services
│   ├── ports/     # Driving (input) & driven (output) interfaces
│   └── adapters/  # GraphQL resolvers, PostgreSQL repos
├── graphql/       # Schema composition, ASGI server
├── db/            # Async SQLAlchemy engine & sessions
├── rust_services/ # Rust crypto + blockchain (Cargo workspace)
├── shared/        # Cross-cutting concerns
├── ml/            # ML module (planned)
└── wallet/        # Wallet module (planned)
```

See [README.architecture.md](./README.architecture.md) for full ADRs, data flows, and module dependency graphs.

## Getting Started

### Prerequisites

- Python 3.13+
- Rust 2024 edition
- PostgreSQL
- Redis & Celery (for ML features)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/ArelyXl/Lidercom-kr-Peru-Platform-ML-Backend.git
cd Lidercom-kr-Peru-Platform-ML-Backend

# 2. Python environment
cd App
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Database
cp db/.env.example db/.env   # configure your DB connection
alembic upgrade head

# 4. Rust services
cd rust_services
cargo build --release

# 5. Run the server
uvicorn graphql.server:app
```

## Project Structure

```
├── App/                    # Main application (production)
│   ├── auth/               # Authentication module
│   ├── db/                 # Database config
│   ├── graphql/            # GraphQL schema & server
│   ├── rust_services/      # Rust crypto/blockchain
│   ├── requirements.txt
│   └── init.sql            # Database schema
├── Test/DBTests/           # MVP prototype
├── README.architecture.md  # Architecture docs & ADRs
└── LICENSE.md              # Proprietary license
```

## License

Proprietary. See [LICENSE.md](./LICENSE.md). Commercial use requires written permission from **ArelyXl & Lidercom (MW Coach inc)**.
