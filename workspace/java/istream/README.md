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
6. [Build](#6-build)
7. [Startup Modes](#7-startup-modes)
   - [Mode A — Local (No Docker)](#mode-a--local-no-docker)
   - [Mode B — Hybrid (Docker infra + local JAR)](#mode-b--hybrid-docker-infra--local-jar)
   - [Mode C — Full Docker](#mode-c--full-docker)
8. [Stop the Application](#8-stop-the-application)
9. [Configuration](#9-configuration)
10. [Settings UI](#10-settings-ui)
11. [Access](#11-access)
12. [Project Structure](#12-project-structure)
13. [API Reference](#13-api-reference)
14. [Adding a New Data Source](#14-adding-a-new-data-source)
15. [Troubleshooting](#15-troubleshooting)
16. [License](#16-license)

---

## 1. Features

- **Plugin data sources** — each source is an independent Spring bean; add one class and register it in the database to enable a new feed
- **Runtime source configuration** — enable/disable sources and change their settings (assets, cities, API keys, poll intervals) live from the Settings UI without restarting
- **Kafka fan-out** — three independent consumer groups (persistence, dashboard, alerts) consume the same topic concurrently
- **Real-time WebSocket push** — browser clients subscribe to `/topic/events/{source}` via STOMP/SockJS for live updates
- **Persistent history** — every event written to PostgreSQL via JPA; queryable with pagination and source/asset filters
- **Configurable alert engine** — rule-based threshold alerts dispatched to pluggable notifiers (email, Telegram, etc.)
- **JWT authentication** — stateless REST API protected by Bearer tokens; roles stored in the database
- **Circuit breakers + retry** — Resilience4j protects each external API call; stale cached data served on open circuit
- **Embedded Kafka option** — the `local` Spring profile starts an in-process KRaft Kafka broker; no Docker required for development
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
│  (Binance API)      (Yahoo Finance)     (OpenWeatherMap)     │
│                                                              │
│   enabled/disabled at runtime via source_settings table      │
└────────┬───────────────────┬───────────────────┬────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │ List<DataSource> (Spring injection)
                             ▼
                  ┌─────────────────────┐
                  │   SourceScheduler   │  polls every N ms (per-source, configurable)
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
| Embedded Kafka | Apache Kafka KRaft | In-process broker for `local` profile (no Docker) |
| Database | PostgreSQL 16 | Persistent event and rule storage |
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
| Kafka broker | **9092** | PLAINTEXT (Docker or embedded) |
| PostgreSQL | **5432** | Native local install |
| PostgreSQL | **5433** | Docker host port (internal: 5432) |
| Prometheus | **9090** | Docker only |
| Grafana | **3002** | Docker only — admin / admin |

> PostgreSQL port 5433 is used when running via Docker Compose to avoid clashing with a local PostgreSQL install on 5432.

---

## 5. Prerequisites

### Mode A — Local (No Docker)

| Tool | Minimum version | Notes |
|---|---|---|
| Java JDK | **21** | https://adoptium.net — must be a JDK, not a JRE |
| Maven | 3.9 | Or use the included `mvnw` / `mvnw.cmd` wrapper |
| PostgreSQL | 16 | https://www.postgresql.org/download/ |

Kafka is **not required** — the `local` Spring profile starts an embedded KRaft Kafka broker automatically.

### Mode B — Hybrid (Docker infra + local JAR)

| Tool | Minimum version |
|---|---|
| Java JDK | **21** |
| Maven | 3.9 (or `mvnw`) |
| Docker Desktop | 24.x |

### Mode C — Full Docker

| Tool | Minimum version |
|---|---|
| Docker Desktop | 24.x |

No local Java or Maven required.

---

## 6. Build

> Skip this step for Mode C (Full Docker) — the Dockerfile builds the JAR inside the container.

### macOS / Linux

```bash
chmod +x mvnw scripts/*.sh
./scripts/setup.sh        # checks Java version, builds, copies .env.example → .env
```

Or build directly:

```bash
./mvnw clean package -DskipTests
```

### Windows

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1       # checks Java version, builds, copies .env.example → .env
```

Or build directly:

```powershell
.\mvnw.cmd clean package -DskipTests
```

The fat JAR is produced at:

```
istream-app/target/istream-app-1.0.0-SNAPSHOT.jar
```

---

## 7. Startup Modes

### Mode A — Local (No Docker)

Starts the application with **embedded KRaft Kafka** and connects to a **local PostgreSQL** on port 5432. No Docker required. This is the fastest way to run in development.

#### Prerequisites — PostgreSQL setup (first time only)

```bash
# macOS / Linux
psql -U postgres -c "CREATE USER istream WITH PASSWORD 'istream';"
psql -U postgres -c "CREATE DATABASE istream OWNER istream;"
```

```powershell
# Windows (PowerShell)
$env:PGPASSWORD = 'postgres'
psql -U postgres -h localhost -c "CREATE USER istream WITH PASSWORD 'istream';"
psql -U postgres -h localhost -c "CREATE DATABASE istream OWNER istream;"
```

Flyway runs on first startup and creates all tables automatically.

#### Start (dedicated scripts)

```bash
# macOS / Linux
./scripts/start-local.sh
```

```powershell
# Windows
.\scripts\start-local.ps1
```

#### Start (via flag on the main script)

```bash
./scripts/start.sh --local
```

```powershell
.\scripts\start.ps1 -Local
```

#### Manual start

```bash
# macOS / Linux
./mvnw clean package -DskipTests
java -jar istream-app/target/istream-app-*.jar --spring.profiles.active=local
```

```powershell
# Windows — set JAVA_HOME explicitly if needed
$env:JAVA_HOME = "C:\Program Files\<your-jdk-21-folder>"
.\mvnw.cmd clean package -DskipTests
java -jar istream-app\target\istream-app-1.0.0-SNAPSHOT.jar --spring.profiles.active=local
```

#### What the `local` profile does

- Starts an embedded KRaft Kafka broker on port 9092 (via `LocalKafkaInitializer`)
- Overrides `DB_URL` to `jdbc:postgresql://localhost:5432/istream`
- Sets `flyway.validate-on-migrate: false` for relaxed schema management
- Enables `DEBUG` logging for `com.istream`

---

### Mode B — Hybrid (Docker infra + local JAR)

Runs Kafka, PostgreSQL, and Redis in Docker and the Spring Boot JAR directly on your machine. Best for debugging with a full infrastructure stack.

#### Start

```bash
# macOS / Linux
./scripts/start.sh
```

```powershell
# Windows
.\scripts\start.ps1
```

The scripts start the Docker services, wait for them to be ready, then launch the JAR with environment variables pointing to the Docker-exposed ports.

#### Manual start

**Step 1 — Start infrastructure**

```bash
docker compose up -d kafka postgres redis
```

Wait ~20 seconds for services to initialise.

**Step 2 — Set environment variables**

```bash
# macOS / Linux
export KAFKA_BROKERS=localhost:9092
export DB_URL=jdbc:postgresql://localhost:5433/istream
export DB_USER=istream
export DB_PASSWORD=istream
export REDIS_HOST=localhost
export JWT_SECRET=dev-secret-change-in-production-minimum-32-chars
```

```powershell
# Windows
$env:KAFKA_BROKERS = "localhost:9092"
$env:DB_URL        = "jdbc:postgresql://localhost:5433/istream"
$env:DB_USER       = "istream"
$env:DB_PASSWORD   = "istream"
$env:REDIS_HOST    = "localhost"
$env:JWT_SECRET    = "dev-secret-change-in-production-minimum-32-chars"
```

**Step 3 — Run**

```bash
java -jar istream-app/target/istream-app-*.jar
```

---

### Mode C — Full Docker

Builds the JAR inside a multi-stage container and starts the full stack with one command.

```bash
# macOS / Linux
docker compose up --build

# Windows
docker compose up --build
```

Or using the script:

```bash
./scripts/start.sh --docker
```

```powershell
.\scripts\start.ps1 -Docker
```

The first build takes 3–5 minutes (Maven downloads dependencies). Subsequent starts are fast.

#### Verify

```bash
curl http://localhost:8080/actuator/health
# {"status":"UP"}
```

---

## 8. Stop the Application

### Local mode (Mode A)

```bash
# macOS / Linux
./scripts/stop-local.sh
```

```powershell
# Windows
.\scripts\stop-local.ps1
```

### Hybrid mode (Mode B)

```bash
# macOS / Linux
./scripts/stop.sh           # stop JAR only
./scripts/stop.sh --infra   # stop JAR + Docker infrastructure
./scripts/stop.sh --all     # alias for --infra
```

```powershell
# Windows
.\scripts\stop.ps1          # stop JAR only
.\scripts\stop.ps1 -Infra   # stop JAR + Docker infrastructure
.\scripts\stop.ps1 -All     # alias for -Infra
```

### Full Docker (Mode C)

```bash
docker compose down        # stop containers, keep volumes
docker compose down -v     # stop containers and delete all data
```

---

## 9. Configuration

Copy `.env.example` to `.env` and adjust values before starting (Modes A and B load this file automatically).

| Variable | Default | Description |
|---|---|---|
| `SERVER_PORT` | `8080` | HTTP server port |
| `KAFKA_BROKERS` | `localhost:9092` | Kafka bootstrap servers (not used in local mode — embedded broker starts automatically) |
| `DB_URL` | `jdbc:postgresql://localhost:5433/istream` | JDBC URL (local mode overrides this to port 5432) |
| `DB_USER` | `istream` | Database username |
| `DB_PASSWORD` | `istream` | Database password |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `JWT_SECRET` | *(dev default)* | JWT signing secret — **change in production** (min 32 chars) |
| `JWT_EXPIRATION_MS` | `86400000` | Token lifetime in milliseconds (24 hours) |
| `SPRING_PROFILES_ACTIVE` | `default` | Set to `local` for no-Docker mode; `prod` for structured JSON logging |

> Source-specific settings (assets, cities, API keys, poll intervals, enabled/disabled) are managed at runtime from the **Settings UI** and stored in the `source_settings` database table. See [Section 10](#10-settings-ui).

---

## 10. Settings UI

Source settings are configured at runtime without restarting the application. Navigate to **http://localhost:8080/settings.html** after signing in.

| Source | Default assets | Default interval | Notes |
|---|---|---|---|
| Crypto | BTC-USD, ETH-USD, SOL-USD | 30 s | Binance public API — no key required |
| Stocks | AAPL, TSLA, MSFT | 30 s | Yahoo Finance — free, no key required |
| Weather | London, New York | 30 s | OpenWeatherMap — requires free API key |

Changes take effect on the next poll cycle. Settings are persisted to PostgreSQL via the `source_settings` table and survive restarts.

### Settings API

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/settings/sources` | Bearer | List all source configurations |
| GET | `/api/v1/settings/sources/{sourceId}` | Bearer | Get one source configuration |
| PUT | `/api/v1/settings/sources/{sourceId}` | Bearer | Update source configuration |

**Example — enable weather source:**

```bash
curl -X PUT http://localhost:8080/api/v1/settings/sources/weather \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceId": "weather",
    "enabled": true,
    "settings": {
      "cities": "London,Tokyo,Sydney",
      "apiKey": "your-openweathermap-key",
      "intervalMs": "60000"
    }
  }'
```

---

## 11. Access

| Resource | URL | Credentials |
|---|---|---|
| Sign-in | http://localhost:8080/index.html | admin / admin123 |
| Dashboard | http://localhost:8080/dashboard.html | JWT (auto-redirect) |
| Settings | http://localhost:8080/settings.html | JWT (auto-redirect) |
| REST API base | http://localhost:8080/api/v1 | JWT Bearer token |
| Swagger UI | http://localhost:8080/swagger-ui.html | — |
| OpenAPI spec | http://localhost:8080/v3/api-docs | — |
| Health check | http://localhost:8080/actuator/health | — |
| Prometheus metrics | http://localhost:8080/actuator/prometheus | — |
| Prometheus UI | http://localhost:9090 | Docker only |
| Grafana | http://localhost:3002 | Docker only — admin / admin |

### Authenticate via API

```bash
# 1. Get a token
curl -s -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq .token

# 2. Use the token
TOKEN=<paste-token-here>
curl http://localhost:8080/api/v1/events?source=crypto \
  -H "Authorization: Bearer $TOKEN"
```

> Default admin password is `admin123`. Change it by inserting a new BCrypt hash via a Flyway migration.

---

## 12. Project Structure

```
istream/
├── pom.xml                              # Parent POM — Spring Boot 3.2, Java 21
├── docker-compose.yml                   # Full stack: Kafka, Postgres, Redis, Prometheus, Grafana
├── .env / .env.example                  # Environment variable template
├── mvnw / mvnw.cmd                      # Maven wrapper — no system Maven required
│
├── scripts/
│   ├── setup.sh / setup.ps1             # Build + prerequisites check
│   ├── start-local.sh / start-local.ps1 # Start: embedded Kafka + local PostgreSQL (no Docker)
│   ├── stop-local.sh  / stop-local.ps1  # Stop local mode instance
│   ├── start.sh / start.ps1             # Start: hybrid (--local / -Local flag) or Docker (-Docker)
│   └── stop.sh  / stop.ps1              # Stop: JAR only, or with --infra / -Infra
│
├── monitoring/
│   └── prometheus.yml                   # Prometheus scrape config
│
├── istream-core/                        # Shared domain — no Spring dependencies
│   └── src/main/java/com/istream/core/
│       ├── model/
│       │   ├── MarketEvent.java         # Canonical message record (Kafka payload)
│       │   └── AlertNotification.java   # Alert dispatch payload
│       ├── source/
│       │   ├── DataSource.java          # Plugin interface: sourceId() + fetch()
│       │   └── SourceSettingProvider.java  # Interface for runtime setting access
│       ├── alert/AlertRule.java         # Plugin interface: matches() + buildNotification()
│       └── notifier/Notifier.java       # Plugin interface: notifierId() + send()
│
├── istream-sources/                     # Data source implementations
│   └── src/main/java/com/istream/sources/
│       ├── CryptoSource.java            # Binance public API — runtime enable/disable
│       ├── StockSource.java             # Yahoo Finance — runtime enable/disable
│       └── WeatherSource.java           # OpenWeatherMap — disabled by default
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
│       │   ├── SettingsController.java  # GET/PUT /api/v1/settings/sources
│       │   └── GlobalExceptionHandler.java
│       ├── dto/
│       │   ├── LoginRequest.java / LoginResponse.java
│       │   └── SourceSettingDto.java    # { sourceId, enabled, settings }
│       ├── security/
│       │   ├── SecurityConfig.java
│       │   ├── JwtService.java
│       │   ├── JwtAuthFilter.java
│       │   └── UserDetailsServiceImpl.java
│       └── websocket/WebSocketConfig.java
│
├── istream-persistence/                 # JPA, repositories, Flyway migrations
│   └── src/main/java/com/istream/persistence/
│       ├── entity/
│       │   ├── MarketEventEntity.java
│       │   ├── AlertRuleEntity.java
│       │   ├── UserEntity.java
│       │   ├── SourceSettingEntity.java # source_settings table entity
│       │   └── SourceSettingId.java     # Composite PK (source_id, setting_key)
│       ├── repository/
│       │   ├── MarketEventRepository.java
│       │   ├── AlertRuleRepository.java
│       │   ├── UserRepository.java
│       │   └── SourceSettingRepository.java
│       └── service/
│           ├── EventPersistenceService.java
│           └── SourceSettingService.java  # Implements SourceSettingProvider; in-memory cache
│   └── src/main/resources/db/migration/
│       ├── V1__init.sql                 # Tables: market_events, alert_rules, users + admin seed
│       └── V2__source_settings.sql      # Table: source_settings + default values
│
└── istream-app/                         # Runnable entry point
    ├── Dockerfile                       # Multi-stage build (Maven + JRE Alpine)
    └── src/main/java/com/istream/app/
        ├── IStreamApplication.java
        ├── LocalKafkaInitializer.java   # Starts embedded KRaft Kafka on "local" profile
        ├── config/
        │   ├── KafkaConfig.java         # Producer, consumer, topic auto-creation
        │   └── RestTemplateConfig.java  # Timeouts + User-Agent interceptor
        ├── producer/GenericProducer.java
        └── scheduler/SourceScheduler.java  # Polls enabled sources in parallel
    └── src/main/resources/
        ├── application.yml
        ├── application-local.yml        # Embedded Kafka, port 5432, relaxed Flyway
        └── logback-spring.xml
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

**Example:**
```bash
curl "http://localhost:8080/api/v1/events?source=crypto&page=0&size=20" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Sources

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/sources` | Bearer | List registered sources and their runtime status |

**Response:**
```json
[
  { "id": "crypto", "status": "active"   },
  { "id": "stocks", "status": "active"   },
  { "id": "weather","status": "disabled" }
]
```

---

### Source Settings

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/settings/sources` | Bearer | All source configurations |
| GET | `/api/v1/settings/sources/{sourceId}` | Bearer | Single source configuration |
| PUT | `/api/v1/settings/sources/{sourceId}` | Bearer | Update source configuration |

**GET response:**
```json
{
  "sourceId": "crypto",
  "enabled": true,
  "settings": {
    "assets": "BTC-USD,ETH-USD,SOL-USD",
    "intervalMs": "30000"
  }
}
```

**PUT request body:**
```json
{
  "sourceId": "crypto",
  "enabled": true,
  "settings": {
    "assets": "BTC-USD,ETH-USD,SOL-USD,BNB-USD",
    "intervalMs": "60000"
  }
}
```

---

### WebSocket — Real-time events

Connect with SockJS + STOMP:

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

Integrating a new feed requires three steps and zero changes to existing pipeline code.

**Step 1 — Implement the interface** (one file in `istream-sources/`):

```java
@Component
public class ForexSource implements DataSource {

    private final SourceSettingProvider settings;
    private List<MarketEvent> lastKnown = List.of();

    public ForexSource(RestTemplate restTemplate, SourceSettingProvider settings) {
        this.settings = settings;
    }

    @Override
    public String sourceId() { return "forex"; }

    @Override
    @CircuitBreaker(name = "forex-source", fallbackMethod = "fetchFallback")
    public List<MarketEvent> fetch() {
        List<String> pairs = settings.getList(sourceId(), "pairs");
        // call your API, return normalised MarketEvent list
        return pairs.stream().map(pair ->
            MarketEvent.builder()
                .source(sourceId()).asset(pair).metric("rate").value(1.085).unit("USD")
                .build()
        ).toList();
    }

    public List<MarketEvent> fetchFallback(Exception e) { return lastKnown; }
}
```

**Step 2 — Seed default settings** via a new Flyway migration (e.g. `V3__forex_source.sql`):

```sql
INSERT INTO source_settings (source_id, setting_key, setting_value) VALUES
  ('forex', 'enabled',    'false'),
  ('forex', 'pairs',      'EUR-USD,GBP-USD'),
  ('forex', 'intervalMs', '30000');
```

**Step 3 — Enable from the Settings UI** (or via the API):

```bash
curl -X PUT http://localhost:8080/api/v1/settings/sources/forex \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sourceId":"forex","enabled":true,"settings":{"pairs":"EUR-USD,GBP-USD","intervalMs":"30000"}}'
```

The scheduler, producer, Kafka topic, all consumers, and the REST API pick it up automatically. The Settings UI also renders it automatically (fields are derived from the database row keys).

---

## 15. Troubleshooting

### JAVA_HOME not set / wrong Java version

```
Error: A fatal exception has occurred. Unrecognized VM option 'MaxRAMPercentage=75.0'
```

This means the scripts picked up a Java 8 JRE instead of JDK 21.

**Fix (Windows):**
```powershell
# Verify which java the shell resolves
Get-Command java | Select-Object -ExpandProperty Source

# Set JAVA_HOME for the session
$env:JAVA_HOME = "C:\Program Files\<your-jdk-21-folder>"
$env:PATH = "$env:JAVA_HOME\bin;" + $env:PATH
java -version   # should show 21
```

**Fix (macOS / Linux):**
```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)   # macOS
export PATH=$JAVA_HOME/bin:$PATH
java -version
```

The `start-local` scripts read `JAVA_HOME` from both the process and machine environment scopes automatically.

---

### Application fails to start — database auth error

```
FATAL: password authentication failed for user "istream"
```

**Fix:** The `istream` PostgreSQL user's password doesn't match `.env`. Reset it:

```bash
psql -U postgres -c "ALTER USER istream WITH PASSWORD 'istream';"
```

---

### Application fails to start — Kafka not available (hybrid mode)

```
org.apache.kafka.common.errors.TimeoutException: Topic not available
```

**Fix:** Kafka takes 15–30 seconds after container start. Wait and retry, or switch to local mode which uses the embedded broker:

```powershell
.\scripts\start-local.ps1
```

---

### Application fails to start — Database migration error

```
FlywayException: Validate failed: Migration checksum mismatch
```

**Fix (local mode):** The `local` profile sets `flyway.validate-on-migrate: false` so this should not occur. If it does, drop and recreate the database:

```bash
psql -U postgres -c "DROP DATABASE istream;"
psql -U postgres -c "CREATE DATABASE istream OWNER istream;"
```

**Fix (Docker):**
```bash
docker compose down -v
docker compose up -d postgres
# wait 10s, then restart the app
```

---

### Port already in use

```
Web server failed to start. Port 8080 was already in use.
```

**Fix:** Change `SERVER_PORT` in `.env`, or find and kill the conflicting process:

```bash
# macOS / Linux
lsof -i :8080 | awk 'NR>1 {print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

### Crypto / stock events not flowing — 429 rate limit

```
WARN CryptoSource - Binance circuit open, using cached data: 429 Too Many Requests
WARN StockSource  - Stock API circuit open, using cached data: 429 Too Many Requests
```

The circuit breaker opens after repeated 429 responses. This typically means the poll interval is too aggressive.

**Fix:** Increase `intervalMs` to `60000` (60 s) from the Settings UI at http://localhost:8080/settings.html. The circuit breaker will close on the next successful call.

---

### JWT token rejected — 401 Unauthorized

1. Call `POST /api/v1/auth/login` to get a fresh token
2. Pass it as `Authorization: Bearer <token>` (not `Basic`)
3. Ensure `JWT_SECRET` is the same value between restarts

---

### Check service health

```bash
# Application
curl http://localhost:8080/actuator/health

# Kafka topic list (Docker)
docker exec -it istream-kafka-1 \
  kafka-topics --bootstrap-server localhost:9092 --list

# PostgreSQL — count persisted events
psql -U istream -h localhost -c "SELECT COUNT(*) FROM market_events;"

# Redis ping (Docker)
docker exec -it istream-redis-1 redis-cli PING
```

---

### Clean reset — local mode

```powershell
# Windows
.\scripts\stop-local.ps1
Remove-Item logs\istream*.log, .istream.pid -ErrorAction SilentlyContinue
```

```bash
# macOS / Linux
./scripts/stop-local.sh
rm -f logs/istream*.log .istream.pid
```

### Clean reset — hybrid or Docker

```bash
./scripts/stop.sh --all
docker compose down -v
rm -f logs/istream*.log .istream.pid
./scripts/setup.sh
./scripts/start.sh
```

---

## 16. License

MIT — see repository root for full license text.
