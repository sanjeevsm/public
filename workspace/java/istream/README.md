# iStream+ — Universal Real-Time Data Streaming Pipeline

Universal real-time data streaming pipeline — Spring Boot 3, Apache Kafka, PostgreSQL, WebSocket, JWT.

Pulls live market and sensor data from pluggable sources (crypto prices, stock quotes, weather), streams every event through Kafka, and fans out to three independent consumer groups: persistent storage, a real-time WebSocket dashboard, and a configurable alert engine. New data sources drop in as a single Java class with no changes to the pipeline.

---

## Table of Contents

1. [Features](#1-features)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Default Ports](#4-default-ports)
5. [Prerequisites](#5-prerequisites)
6. [Docker (Recommended)](#6-docker-recommended)
7. [Quick Start (Process-Based)](#7-quick-start-process-based)
8. [Configuration](#8-configuration)
9. [Start the Application](#9-start-the-application)
10. [Stop the Application](#10-stop-the-application)
11. [Access](#11-access)
12. [Project Structure](#12-project-structure)
13. [API Reference](#13-api-reference)
14. [Adding a New Data Source](#14-adding-a-new-data-source)
15. [Troubleshooting](#15-troubleshooting)
16. [License](#16-license)

---

## 1. Features

- **Plugin data sources** — each source is an independent Spring bean; add one class and one YAML entry to enable a new feed
- **Kafka fan-out** — three independent consumer groups (persistence, dashboard, alerts) consume the same topic concurrently
- **Real-time WebSocket push** — browser clients subscribe to `/topic/events/{source}` via STOMP/SockJS for live updates
- **Persistent history** — every event written to PostgreSQL via JPA; queryable with pagination and source/asset filters
- **Configurable alert engine** — rule-based threshold alerts dispatched to pluggable notifiers (email, Telegram, etc.)
- **JWT authentication** — stateless REST API protected by Bearer tokens; roles stored in the database
- **Circuit breakers + retry** — Resilience4j protects each external API call; stale cached data served on open circuit
- **Metrics and monitoring** — Micrometer → Prometheus → Grafana; all endpoints scraped automatically
- **OpenAPI 3 documentation** — Swagger UI auto-generated from controller annotations
- **Graceful shutdown** — in-flight requests drained before process exit
- **Cross-platform** — runs as a fat JAR on any OS with Java 21+; full stack via Docker Compose

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Data Sources                          │
│                                                              │
│   CryptoSource         StockSource         WeatherSource     │
│  (CoinGecko API)    (Yahoo Finance API)  (OpenWeatherMap)    │
│  @ConditionalOn...   @ConditionalOn...   @ConditionalOn...   │
└────────┬───────────────────┬───────────────────┬────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │ List<DataSource> (Spring injection)
                             ▼
                  ┌─────────────────────┐
                  │   SourceScheduler   │  polls every N seconds
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   GenericProducer   │  source-agnostic
                  └──────────┬──────────┘
                             │
                             ▼
          ┌──────────────────────────────────────┐
          │       Kafka Topic                    │
          │   istream.market.events              │
          │   (3 partitions, key: source:asset)  │
          └────────┬────────────┬────────────────┘
                   │            │            │
    ┌──────────────┘    ┌───────┘    ┌───────┘
    │                   │            │
    ▼                   ▼            ▼
┌───────────┐   ┌───────────────┐  ┌───────────────────┐
│  Alert    │   │   Dashboard   │  │  EventPersistence │
│  Engine   │   │   Consumer    │  │  Service          │
│ (group 1) │   │  (group 2)    │  │  (group 3)        │
└─────┬─────┘   └───────┬───────┘  └────────┬──────────┘
      │                 │                    │
      ▼                 ▼                    ▼
┌──────────┐   ┌────────────────┐   ┌───────────────┐
│Notifiers │   │ WebSocket      │   │  PostgreSQL   │
│(email/TG)│   │ /topic/events/ │   │  (JPA + JDBC) │
└──────────┘   └───────┬────────┘   └───────────────┘
                       │
                       ▼
              ┌──────────────────────────┐
              │     REST API Layer       │
              │  Spring Web MVC          │
              │  Spring Security (JWT)   │
              │  OpenAPI / Swagger UI    │
              │  Spring Actuator         │
              └──────────────────────────┘
```

**Consumer group isolation** — each group maintains its own Kafka offset, so the dashboard, alert engine, and persistence layer each see every event independently and can be scaled or restarted without affecting the others.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Java 21 | LTS release with records, sealed classes |
| Framework | Spring Boot 3.2 | Auto-configuration, embedded Tomcat |
| Messaging | Apache Kafka 7.6 | Durable, ordered, partitioned event stream |
| Database | PostgreSQL 16 | Persistent event and rule storage |
| Cache/Session | Redis 7 | Future rate-limiting and session support |
| Security | Spring Security + jjwt 0.12 | Stateless JWT auth |
| Resilience | Resilience4j 2.2 | Circuit breaker, retry, rate limiter |
| Monitoring | Micrometer + Prometheus + Grafana | Metrics collection and dashboards |
| API Docs | Springdoc OpenAPI 3 | Auto-generated Swagger UI |
| Build | Maven 3.9 multi-module | Modular dependency management |
| Container | Docker + Docker Compose | Reproducible full-stack deployment |

---

## 4. Default Ports

| Service | Host Port | Notes |
|---|---:|---|
| iStream+ API | **8080** | REST + WebSocket |
| Kafka broker | **9092** | PLAINTEXT |
| PostgreSQL | **5433** | Host port (internal: 5432) |
| Redis | **6379** | |
| Prometheus | **9090** | |
| Grafana | **3002** | admin / admin |

> Ports 5433 and 3002 are deliberately offset to avoid clashes with other projects in this repository (iCare+ uses 5432; iTrack+ uses 3000).

---

## 5. Prerequisites

### Docker (Recommended)

| Tool | Minimum version | Install |
|---|---|---|
| Docker Desktop | 24.x | https://docs.docker.com/get-docker/ |
| Docker Compose | 2.x (bundled) | Included with Docker Desktop |

### Process-Based (Hybrid)

| Tool | Minimum version | Install |
|---|---|---|
| Java (JDK) | 21 | https://adoptium.net |
| Maven | 3.9 (or use included `mvnw`) | https://maven.apache.org/download.cgi |
| Docker Desktop | 24.x | For running Kafka, PostgreSQL, Redis |

### Fully Local (No Docker)

Same as above, plus:

| Tool | Minimum version | Notes |
|---|---|---|
| Apache Kafka | 3.7 | https://kafka.apache.org/downloads |
| PostgreSQL | 16 | https://www.postgresql.org/download/ |
| Redis | 7 | https://redis.io/docs/install/ |

---

## 6. Docker (Recommended)

The Docker method builds the JAR inside a multi-stage container and starts the full stack with one command. No local Java or Maven installation required.

### macOS / Linux

```bash
git clone <repo-url>
cd workspace/java/istream
docker compose up --build
```

### Windows

```powershell
git clone <repo-url>
cd workspace\java\istream
docker compose up --build
```

The first build takes 3–5 minutes (Maven downloads dependencies). Subsequent starts are fast.

### Verify

```bash
curl http://localhost:8080/actuator/health
# {"status":"UP"}
```

### URLs

| Service | URL |
|---|---|
| API | http://localhost:8080/api/v1 |
| Swagger UI | http://localhost:8080/swagger-ui.html |
| Health check | http://localhost:8080/actuator/health |
| Metrics | http://localhost:8080/actuator/prometheus |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3002 — admin / admin |

### Stop (Docker)

```bash
docker compose down          # stop containers, keep volumes
docker compose down -v       # stop containers and delete all data
```

---

## 7. Quick Start (Process-Based)

The process-based method runs Docker only for infrastructure (Kafka, PostgreSQL, Redis) and starts the Spring Boot JAR directly on your machine. This is the recommended approach for development and debugging.

### Prerequisites check

Verify your environment before running setup:

```bash
java -version    # must show 21+
./mvnw --version # Maven wrapper — no system Maven required
docker --version # must show 24+
```

### macOS / Linux — setup

```bash
chmod +x mvnw scripts/setup.sh scripts/start.sh scripts/stop.sh
./scripts/setup.sh
```

`setup.sh` checks Java version, builds the project using `mvnw` (`mvn clean package -DskipTests`), and copies `.env.example` → `.env`.

### macOS / Linux — start

```bash
# Hybrid (recommended): Docker infra + local JAR
./scripts/start.sh

# Full Docker: everything in containers
./scripts/start.sh --docker
```

### Windows — setup

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```

### Windows — start

```powershell
# Hybrid (recommended): Docker infra + local JAR
.\scripts\start.ps1

# Full Docker: everything in containers
.\scripts\start.ps1 -Docker
```

### Manual start (any OS)

If you prefer to start without the scripts:

**Step 1 — Start infrastructure**

```bash
docker compose up -d zookeeper kafka postgres redis
```

Wait ~20 seconds for services to initialise.

**Step 2 — Build**

```bash
./mvnw clean package -DskipTests
```

**Step 3 — Set environment variables**

macOS / Linux:
```bash
export KAFKA_BROKERS=localhost:9092
export DB_URL=jdbc:postgresql://localhost:5433/istream
export DB_USER=istream
export DB_PASSWORD=istream
export REDIS_HOST=localhost
export JWT_SECRET=dev-secret-change-in-production-minimum-32-chars
```

Windows (PowerShell):
```powershell
$env:KAFKA_BROKERS = "localhost:9092"
$env:DB_URL        = "jdbc:postgresql://localhost:5433/istream"
$env:DB_USER       = "istream"
$env:DB_PASSWORD   = "istream"
$env:REDIS_HOST    = "localhost"
$env:JWT_SECRET    = "dev-secret-change-in-production-minimum-32-chars"
```

**Step 4 — Run**

```bash
java -jar istream-app/target/istream-app-*.jar
```

### Fully Local (No Docker)

For environments where Docker is unavailable:

**Kafka** (macOS / Linux):
```bash
# Download and extract Kafka 3.7+
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server.properties &
```

**PostgreSQL**:
```bash
# Create database and user
psql -U postgres -c "CREATE USER istream WITH PASSWORD 'istream';"
psql -U postgres -c "CREATE DATABASE istream OWNER istream;"
```

**Redis**:
```bash
redis-server &
```

Then set `DB_URL=jdbc:postgresql://localhost:5432/istream` (note: 5432, not 5433, when PostgreSQL runs natively) and start the JAR as shown in Step 4.

---

## 8. Configuration

Copy `.env.example` to `.env` and adjust values before starting.

| Variable | Default | Description |
|---|---|---|
| `SERVER_PORT` | `8080` | HTTP server port |
| `KAFKA_BROKERS` | `localhost:9092` | Kafka bootstrap servers (comma-separated) |
| `DB_URL` | `jdbc:postgresql://localhost:5433/istream` | JDBC connection URL |
| `DB_USER` | `istream` | Database username |
| `DB_PASSWORD` | `istream` | Database password |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `JWT_SECRET` | *(dev default)* | JWT signing secret — **change in production** (min 32 chars) |
| `JWT_EXPIRATION_MS` | `86400000` | Token lifetime in milliseconds (24 hours) |
| `CRYPTO_ENABLED` | `true` | Enable cryptocurrency price source |
| `CRYPTO_ASSETS` | `BTC-USD,ETH-USD,SOL-USD` | Assets to poll from CoinGecko |
| `STOCKS_ENABLED` | `true` | Enable stock price source |
| `STOCK_ASSETS` | `AAPL,TSLA,MSFT` | Ticker symbols to poll from Yahoo Finance |
| `WEATHER_ENABLED` | `false` | Enable weather source (requires API key) |
| `WEATHER_CITIES` | `London,New York` | Cities to poll when weather source is enabled |
| `OPENWEATHER_API_KEY` | *(empty)* | OpenWeatherMap API key — required when `WEATHER_ENABLED=true` |
| `POLL_INTERVAL_MS` | `5000` | Global poll interval in milliseconds |
| `SPRING_PROFILES_ACTIVE` | `default` | Set to `prod` for structured JSON logging |

> All variables have safe defaults for local development. In production, override `JWT_SECRET`, `DB_PASSWORD`, and any external service credentials.

---

## 9. Start the Application

### macOS / Linux

```bash
./scripts/start.sh           # hybrid: Docker infra + local JAR (default)
./scripts/start.sh --docker  # full Docker Compose stack
```

### Windows

```powershell
.\scripts\start.ps1          # hybrid: Docker infra + local JAR (default)
.\scripts\start.ps1 -Docker  # full Docker Compose stack
```

### Logs (process-based)

Application logs are written to `logs/istream.log` in the project root.

```bash
tail -f logs/istream.log
```

### Logs (Docker)

```bash
docker compose logs -f app
```

---

## 10. Stop the Application

### macOS / Linux

```bash
./scripts/stop.sh          # stop JAR only
./scripts/stop.sh --infra  # stop JAR + Docker infrastructure
./scripts/stop.sh --all    # alias for --infra
```

### Windows

```powershell
.\scripts\stop.ps1          # stop JAR only
.\scripts\stop.ps1 -Infra  # stop JAR + Docker infrastructure
.\scripts\stop.ps1 -All    # alias for -Infra
```

### Docker (full stack)

```bash
docker compose down        # stop and remove containers
docker compose down -v     # also remove volumes (deletes all data)
```

---

## 11. Access

| Resource | URL | Credentials |
|---|---|---|
| REST API base | http://localhost:8080/api/v1 | JWT Bearer token |
| Swagger UI | http://localhost:8080/swagger-ui.html | — |
| OpenAPI spec | http://localhost:8080/v3/api-docs | — |
| Health check | http://localhost:8080/actuator/health | — |
| Prometheus metrics | http://localhost:8080/actuator/prometheus | — |
| Prometheus UI | http://localhost:9090 | — |
| Grafana | http://localhost:3002 | admin / admin |

### Authenticate via API

```bash
# 1. Get a token (default user seeded by Flyway)
curl -s -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq .token

# 2. Use the token
TOKEN=<paste-token-here>
curl http://localhost:8080/api/v1/events?source=crypto \
  -H "Authorization: Bearer $TOKEN"
```

> Default admin password is `admin123`. Change it immediately by updating the BCrypt hash in a new Flyway migration.

---

## 12. Project Structure

```
istream/
├── pom.xml                              # Parent POM — Spring Boot 3.2, Java 21
├── docker-compose.yml                   # Full stack: Kafka, Postgres, Redis, Prometheus, Grafana
├── .env.example                         # Environment variable template
├── mvnw / mvnw.cmd                      # Maven wrapper — no system Maven required
├── .gitignore
│
├── scripts/
│   ├── setup.sh / setup.ps1             # Build + prerequisites check
│   ├── start.sh / start.ps1             # Start (hybrid or full Docker)
│   └── stop.sh  / stop.ps1             # Stop (JAR only or with infra)
│
├── monitoring/
│   └── prometheus.yml                   # Prometheus scrape config
│
├── istream-core/                        # Shared domain — no Spring dependencies
│   └── src/main/java/com/istream/core/
│       ├── model/
│       │   ├── MarketEvent.java         # Canonical message record (Kafka payload)
│       │   └── AlertNotification.java   # Alert dispatch payload
│       ├── source/DataSource.java       # Plugin interface: sourceId() + fetch()
│       ├── alert/AlertRule.java         # Plugin interface: matches() + buildNotification()
│       └── notifier/Notifier.java       # Plugin interface: notifierId() + send()
│
├── istream-sources/                     # Data source implementations
│   └── src/main/java/com/istream/sources/
│       ├── CryptoSource.java            # CoinGecko — enabled when sources.crypto.enabled=true
│       ├── StockSource.java             # Yahoo Finance — enabled when sources.stocks.enabled=true
│       ├── WeatherSource.java           # OpenWeatherMap — disabled by default
│       └── config/SourceProperties.java # @ConfigurationProperties binding
│
├── istream-consumers/                   # Kafka consumer group implementations
│   └── src/main/java/com/istream/consumers/
│       ├── AlertEngine.java             # Matches events to rules; dispatches notifications
│       └── DashboardConsumer.java       # Pushes events to WebSocket /topic/events/{source}
│
├── istream-api/                         # REST API, security, WebSocket
│   └── src/main/java/com/istream/api/
│       ├── controller/
│       │   ├── AuthController.java      # POST /api/v1/auth/login
│       │   ├── EventController.java     # GET /api/v1/events (paginated)
│       │   ├── SourceController.java    # GET /api/v1/sources
│       │   └── GlobalExceptionHandler.java
│       ├── security/
│       │   ├── SecurityConfig.java      # Filter chain, CSRF off, stateless sessions
│       │   ├── JwtService.java          # Token generation and validation
│       │   ├── JwtAuthFilter.java       # Bearer token extraction
│       │   └── UserDetailsServiceImpl.java
│       ├── websocket/WebSocketConfig.java
│       └── dto/LoginRequest.java / LoginResponse.java
│
├── istream-persistence/                 # JPA, repositories, Flyway migrations
│   └── src/main/java/com/istream/persistence/
│       ├── entity/
│       │   ├── MarketEventEntity.java
│       │   ├── AlertRuleEntity.java
│       │   └── UserEntity.java
│       ├── repository/
│       │   ├── MarketEventRepository.java
│       │   ├── AlertRuleRepository.java
│       │   └── UserRepository.java
│       └── service/EventPersistenceService.java
│   └── src/main/resources/db/migration/
│       └── V1__init.sql                 # Tables: market_events, alert_rules, users
│
└── istream-app/                         # Runnable entry point
    ├── Dockerfile                       # Multi-stage build (Maven + JRE Alpine)
    ├── src/main/java/com/istream/app/
    │   ├── IStreamApplication.java
    │   ├── LocalKafkaInitializer.java   # Embedded KRaft Kafka for "local" profile
    │   ├── config/
    │   │   ├── KafkaConfig.java         # Producer, consumer, topic auto-creation
    │   │   └── RestTemplateConfig.java  # Timeouts for external HTTP calls
    │   ├── producer/GenericProducer.java # Sends MarketEvent to Kafka
    │   └── scheduler/SourceScheduler.java # Polls all DataSource beans in parallel
    └── src/main/resources/
        ├── application.yml              # All config (env-var overridable)
        ├── application-local.yml        # Local profile: embedded Kafka + relaxed validation
        └── logback-spring.xml           # Console (dev) + JSON (prod) logging
```

---

## 13. API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/login` | None | Returns JWT token |

**Request:**
```json
{ "username": "admin", "password": "admin123" }
```

**Response:**
```json
{ "token": "eyJ...", "type": "Bearer", "expiresInMs": 86400000 }
```

---

### Market Events

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/events` | Bearer | Paginated list; filter by `?source=` and/or `?asset=` |
| GET | `/api/v1/events/latest/{source}/{asset}` | Bearer | Most recent event for a source+asset pair |

**Example — list crypto events:**
```bash
curl "http://localhost:8080/api/v1/events?source=crypto&page=0&size=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "content": [
    {
      "id": "uuid",
      "source": "crypto",
      "asset": "BTC-USD",
      "metric": "price",
      "value": 62400.50,
      "unit": "USD",
      "occurredAt": "2026-08-26T10:00:00Z"
    }
  ],
  "totalElements": 1200,
  "page": 0,
  "size": 20
}
```

---

### Sources

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/sources` | Bearer | List active data sources |

**Response:**
```json
[
  { "id": "crypto", "status": "active" },
  { "id": "stocks", "status": "active" }
]
```

---

### WebSocket — Real-time events

Connect with SockJS + STOMP, then subscribe to a topic:

```javascript
const client = new StompJs.Client({ webSocketFactory: () => new SockJS('/ws') });
client.activate();

// All sources
client.subscribe('/topic/events/all', msg => console.log(JSON.parse(msg.body)));

// Single source
client.subscribe('/topic/events/crypto', msg => console.log(JSON.parse(msg.body)));
```

---

### Management endpoints

| Endpoint | Description |
|---|---|
| `GET /actuator/health` | Liveness / readiness (public) |
| `GET /actuator/metrics` | JVM, HTTP, Kafka metrics |
| `GET /actuator/prometheus` | Prometheus scrape format |
| `GET /actuator/loggers` | Runtime log-level adjustment |

---

## 14. Adding a New Data Source

Integrating a new feed requires only three steps and zero changes to existing code.

**Step 1 — Implement the interface** (one file in `istream-sources/`):

```java
// src/main/java/com/istream/sources/ForexSource.java
@Component
@ConditionalOnProperty(prefix = "sources.forex", name = "enabled", havingValue = "true")
public class ForexSource implements DataSource {

    @Override
    public String sourceId() { return "forex"; }

    @Override
    @CircuitBreaker(name = "forex-source", fallbackMethod = "fetchFallback")
    public List<MarketEvent> fetch() {
        // call your API, return normalised MarketEvent list
        return List.of(
            MarketEvent.builder()
                .source("forex").asset("EUR-USD").metric("rate").value(1.0852).unit("USD")
                .build()
        );
    }

    public List<MarketEvent> fetchFallback(Exception e) { return lastKnown; }
}
```

**Step 2 — Add config binding** in `SourceProperties.java`:

```java
public record SourceProperties(
    CryptoConfig crypto,
    StockConfig stocks,
    WeatherConfig weather,
    ForexConfig forex      // ← add this record
) {
    public record ForexConfig(boolean enabled, List<String> pairs, long intervalMs) {}
}
```

**Step 3 — Enable in `application.yml`**:

```yaml
sources:
  forex:
    enabled: true
    pairs: [EUR-USD, GBP-USD]
    interval-ms: 10000
```

Spring auto-discovers the new bean. The scheduler, producer, Kafka topic, all consumers, and the REST API pick it up with no changes.

---

## 15. Troubleshooting

### Application fails to start — Kafka not available

```
org.apache.kafka.common.errors.TimeoutException: Topic not available
```

**Fix:** Kafka takes 15–30 seconds to be ready after container start. Wait and retry, or increase `start_period` in `docker-compose.yml`.

```bash
docker compose logs kafka | tail -20
# Look for: started (kafka.server.KafkaServer)
```

---

### Application fails to start — Database migration error

```
FlywayException: Validate failed: Migration checksum mismatch
```

**Fix:** The database schema has drifted from the migration scripts. To reset (destroys all data):

```bash
docker compose down -v
docker compose up -d postgres
# wait 10s, then restart app
docker compose up -d app
```

---

### Port already in use

```
Web server failed to start. Port 8080 was already in use.
```

**Fix:** Change `SERVER_PORT` in `.env` or identify and stop the conflicting process:

```bash
# macOS / Linux
lsof -i :8080
kill -9 <PID>

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

### CoinGecko / Yahoo Finance returns empty events

CoinGecko has a public rate limit (~10–30 req/min). Signs:

```
WARN  CryptoSource - CoinGecko circuit open, using cached data: 429 Too Many Requests
```

**Fix:** Increase `POLL_INTERVAL_MS` to at least `30000` (30 seconds) or obtain a CoinGecko API key and set it via a custom HTTP header in `CryptoSource`.

---

### JWT token rejected — 401 Unauthorized

Ensure you:
1. Call `POST /api/v1/auth/login` to get a fresh token
2. Pass it as `Authorization: Bearer <token>` (not `Basic`)
3. Check `JWT_SECRET` is the same between restarts (token is invalid if the secret changes)

---

### Check service health

```bash
# Application
curl http://localhost:8080/actuator/health

# Kafka topic list
docker exec -it istream-kafka-1 \
  kafka-topics --bootstrap-server localhost:9092 --list

# PostgreSQL table count
docker exec -it istream-postgres-1 \
  psql -U istream -c "SELECT COUNT(*) FROM market_events;"

# Redis ping
docker exec -it istream-redis-1 redis-cli PING
```

---

### Reinstall (clean reset — process-based)

```bash
./scripts/stop.sh --all
docker compose down -v
rm -f logs/istream.log logs/istream-err.log .istream.pid
./mvnw clean
./scripts/setup.sh
./scripts/start.sh
```

### Reinstall (clean reset — Docker)

```bash
docker compose down -v
docker compose up --build
```

---

## 16. License

MIT — see repository root for full license text.
