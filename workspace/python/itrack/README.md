# iTrack+ - Personal Finance Tracker

> A complete, production-ready personal finance tracker with multi-user collaboration, multi-currency support, privacy controls, and real-time financial reporting.

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]() [![Version](https://img.shields.io/badge/version-2.1.0-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]()

**Built with:** FastAPI • React • TypeScript • MongoDB • Docker

---

## 📋 Table of Contents

- [Features](#-features)
- [What's New](#-whats-new-v21)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture--tech-stack)
- [Multi-Currency Support](#-multi-currency-support)
- [Entity Management](#-entity-management)
- [Asset & Liability Tracking](#-asset--liability-tracking)
- [Forecasting](#-financial-forecasting)
- [Net Worth Dashboard](#-net-worth-dashboard)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Features

### Core Features

#### 💰 Personal Finance Tracking
- ✅ Track income, expenses, assets, and liabilities
- ✅ **Multi-currency support** - Track finances in 27+ currencies (GBP, USD, EUR, INR, JPY, etc.)
- ✅ **Currency-specific dashboards** - View finances per currency with separate tabs
- ✅ **Net Worth calculation** - Automatic calculation including all assets and liabilities
- ✅ Real-time balance calculations and financial summaries
- ✅ Category-based analytics and breakdown
- ✅ Date-based transaction history
- ✅ CSV import/export for data portability
- ✅ Visual charts and graphs (Chart.js integration)

#### 📈 Advanced Financial Management
- ✅ **Asset Tracking** - Track Cash, Investments, Property, Valuables
- ✅ **Liability Tracking** - Track Mortgages, Loans, Credit Cards
- ✅ **Financial Forecasting** - 6-month projections with 3 scenarios (optimistic, base, pessimistic)
- ✅ **Recurring Transactions** - Automatic monthly recurring income/expenses
- ✅ **Budget Management** - Set limits, track progress, receive alerts
- ✅ **Category Management** - Custom categories with icons and colors

#### 🌍 Multi-Currency Features
- ✅ **27+ Supported Currencies** - Major world currencies including USD, EUR, GBP, INR, JPY, AUD, CAD, SGD, CHF, CNY, HKD, and more
- ✅ **Primary Currency** - Set your main currency (default: USD)
- ✅ **Multi-Currency Selection** - Select multiple currencies to track
- ✅ **Currency-Specific Dashboards** - Separate views for each currency
- ✅ **Currency Tabs** - Easy switching between currencies in Income/Expense/Asset/Liability screens
- ✅ **Currency Selector in Forecast** - View forecast for any selected currency
- ✅ **Consolidated Net Worth** - View net worth per currency or consolidated across all currencies

#### 👥 Multi-User Collaboration (Entity Management)
- ✅ **Create Entities**: Households, Offices, or Custom groups
- ✅ **Invite Members**: Add family members, team members, or collaborators
- ✅ **Role-Based Access**: Admin (full control) vs Member (limited access)
- ✅ **Shared Transactions**: Visible to all entity members
- ✅ **Private Transactions**: Visible only to creator and admins
- ✅ **Entity Dashboard**: Real-time financial overview for the group
- ✅ **Member Management**: Invite, remove, promote, or demote members
- ✅ **Entity-Level Currency Selection** - View entity finances per currency

#### 🔒 Privacy & Security
- ✅ **Transaction Privacy Modes**:
  - 🔒 **Private**: Only you and entity admins can see
  - 👥 **Shared**: All entity members can see
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **HTTP-only Cookies**: XSS protection
- ✅ **Password Hashing**: Bcrypt encryption
- ✅ **CORS Protection**: Configurable origins

---

## 🎉 What's New (v2.1)

### Multi-Currency Support
- 🌍 **27+ Currency Support** - Track finances in multiple currencies simultaneously
- 💱 **Currency Tabs** - Separate tabs for each currency in all transaction screens
- 📊 **Multi-Currency Dashboard** - View all currencies side-by-side or focus on one
- 🎯 **Currency Selector** - Quick currency switching in Dashboard and Forecast views
- 🔄 **Primary Currency** - Set your default currency (auto-selected in tabs)

### Enhanced Financial Tracking
- 📈 **Assets & Liabilities** - New screens for comprehensive financial tracking
- 💰 **Net Worth Calculation** - Automatic calculation: (Income - Expenses) + (Assets - Liabilities)
- 📊 **Net Worth Dashboard** - Prominent display with detailed calculation breakdown
- 🎨 **Theme-Aware Design** - Net Worth card visible on all themes (light, dark, custom)

### Advanced Forecasting
- 🔮 **6-Month Financial Forecast** - Predict future finances based on recurring transactions
- 📉 **3 Scenarios** - Optimistic, Base, Pessimistic projections
- 💱 **Currency-Aware Forecasting** - Separate forecasts for each currency
- 📊 **Visual Charts** - Interactive charts showing projected balances
- 📋 **Monthly Breakdown** - Detailed month-by-month projections

### Default Categories
- **Assets**: Cash, Investments, Property, Valuables
- **Liabilities**: Mortgages, Loans, Credit Cards
- **Income**: Salary, Freelance, Business, Investments, Rental Income
- **Expense**: Rent, Groceries, Utilities, Transportation, Entertainment

### UI/UX Improvements
- 🎨 **Multi-Currency Cards** - Compact cards showing Net Worth for each currency
- 🔄 **Auto-Select Primary Currency** - Primary currency always selected first
- 📱 **Responsive Design** - Optimized for mobile, tablet, and desktop
- 🎯 **Currency Dropdown** - Easy currency selection in all views
- 🌈 **Theme Compatibility** - Works seamlessly with all light and dark themes

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (20.10+ recommended)
- **4GB RAM** available
- **10GB** free disk space
- Ports **3000**, **8002**, and **27017** available

### Installation Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd itrack

# 2. Create environment file
cp .env.example .env

# 3. Start application with Docker
docker-compose up --build

# 4. Wait 30-60 seconds for services to initialize

# 5. Access the application
Frontend:  http://localhost:3000
Backend:   http://localhost:8002
API Docs:  http://localhost:8002/docs
```

### First Time Setup

1. **Register Account**: Open http://localhost:3000 and click "Register"
2. **Setup Currencies**:
   ```
   Settings → Active Currencies → Select: GBP, USD, EUR, INR, etc.
   Settings → Primary Currency → Choose: GBP (or your preferred currency)
   ```
3. **Add First Transaction**:
   ```
   Dashboard → Add Transaction
   Description: "Monthly Salary"
   Amount: 5000
   Type: Income
   Category: Salary
   Currency: GBP (auto-selected)
   ```
4. **Add Assets** (Optional):
   ```
   Assets → Add Asset
   Description: "Savings Account"
   Amount: 10000
   Category: Cash
   Currency: GBP
   ```

### Quick Scripts

**Windows (PowerShell):**
```powershell
.\scripts\verify.ps1         # Verify Docker installation
.\scripts\start.ps1          # Start with Docker
.\scripts\stop.ps1           # Stop containers
```

**Linux/macOS (Bash):**
```bash
./scripts/verify.sh          # Verify Docker installation
./scripts/start.sh           # Start with Docker
./scripts/stop.sh            # Stop containers
```

### Reinstallation (Clean Reset)

The steps above are for a **first-time install**. Reinstallation differs by mode.

**Docker mode.** `docker-compose up` alone reuses the existing MongoDB volumes, so your data survives a restart. For a true clean reinstall that also wipes the database, tear down with `-v` to drop the named volumes (`mongodb_data`, `mongodb_config`), then rebuild:

```bash
docker-compose down -v          # stops containers AND deletes MongoDB volumes
docker-compose up --build        # rebuilds images from scratch
```

To rebuild images without losing data, omit `-v`: `docker-compose down && docker-compose up --build`.

**Local mode** (after `./scripts/setup-local.sh`). Remove the backend virtualenv, frontend packages, generated env files, and runtime artifacts, then re-run setup:

```bash
# macOS / Linux
./scripts/stop-local.sh
rm -rf backend/venv frontend/node_modules .env frontend/.env logs .pids
find backend -type d -name __pycache__ -prune -exec rm -rf {} +
./scripts/setup-local.sh && ./scripts/start-local.sh
```

```powershell
# Windows (PowerShell)
.\scripts\stop-local.ps1
Remove-Item -Recurse -Force backend\venv, frontend\node_modules, .env, frontend\.env, logs, .pids -ErrorAction SilentlyContinue
Get-ChildItem backend -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
.\scripts\setup-local.ps1 ; .\scripts\start-local.ps1
```

> Local mode does not stop MongoDB. If you run Mongo in Docker, clear its data separately with `docker-compose down -v`. To refresh only Python or Node dependencies, delete just `backend/venv` or `frontend/node_modules` and re-run `setup-local`.

---

## 🏗️ Architecture & Tech Stack

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (React)                   │
├─────────────────────────────────────────────────────┤
│  Components:                                        │
│  ├─ Dashboard (Multi-Currency View)                │
│  ├─ Income/Expense/Asset/Liability Management      │
│  ├─ Currency Tabs                                  │
│  ├─ Net Worth Display                              │
│  ├─ Forecast View                                  │
│  └─ Settings                                       │
│                                                     │
│  State Management:                                 │
│  ├─ AuthContext (user, authentication)            │
│  └─ SettingsContext (currency, theme)             │
│                                                     │
│  Services:                                         │
│  ├─ transactionService                             │
│  ├─ entityService                                  │
│  └─ categoryService                                │
└──────────────────┬──────────────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────────────┐
│                 BACKEND (FastAPI)                   │
├─────────────────────────────────────────────────────┤
│  API Routes:                                        │
│  ├─ /api/auth (login, register)                   │
│  ├─ /api/transactions (CRUD + currency filter)     │
│  ├─ /api/entities (collaboration)                  │
│  ├─ /api/categories (customization)                │
│  └─ /api/budgets (tracking)                        │
│                                                     │
│  Services:                                         │
│  ├─ TransactionService                             │
│  │   ├─ get_transactions(currency)                 │
│  │   ├─ get_summary(currency)                      │
│  │   └─ calculate_net_worth()                      │
│  ├─ EntityService                                  │
│  ├─ CategoryService                                │
│  └─ BudgetService                                  │
└──────────────────┬──────────────────────────────────┘
                   │ Motor (Async Driver)
┌──────────────────▼──────────────────────────────────┐
│                DATABASE (MongoDB)                   │
├─────────────────────────────────────────────────────┤
│  Collections:                                       │
│  ├─ users                                          │
│  ├─ transactions (with currency field)             │
│  ├─ entities                                       │
│  ├─ categories (with type field)                   │
│  └─ budgets                                        │
└─────────────────────────────────────────────────────┘
```

### Database Schema

**Transactions Collection:**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  entity_id: ObjectId (optional),
  description: String,
  amount: Float,
  type: "income" | "expense" | "asset" | "liability",
  category: String,
  currency: "USD" | "GBP" | "EUR" | "INR" | ...,  // NEW
  date: DateTime,
  mode: "private" | "shared",
  is_recurring: Boolean,
  recurrence: "monthly" (optional),
  recurrence_start: DateTime (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

**Categories Collection:**
```javascript
{
  _id: ObjectId,
  name: String,
  type: "income" | "expense" | "asset" | "liability" | "both",  // EXTENDED
  color: String (hex),
  icon: String (emoji),
  description: String (optional),
  is_default: Boolean,
  user_id: ObjectId (null for defaults),
  entity_id: ObjectId (optional),
  created_at: DateTime
}
```

### Net Worth Calculation Logic

```python
# Backend calculation
async def get_summary(user_id, currency="USD"):
    # Aggregate by type for specific currency
    results = await collection.aggregate([
        {"$match": {
            "user_id": ObjectId(user_id),
            "currency": currency
        }},
        {"$group": {
            "_id": "$type",
            "total": {"$sum": "$amount"}
        }}
    ]).to_list()

    # Extract totals
    income = get_total(results, "income")
    expense = get_total(results, "expense")
    assets = get_total(results, "asset")
    liabilities = get_total(results, "liability")

    # Calculate
    balance = income - expense
    net_assets = assets - liabilities
    net_worth = balance + net_assets

    return TransactionSummary(
        total_balance=balance,
        total_income=income,
        total_expense=expense,
        total_assets=assets,
        total_liabilities=liabilities,
        net_worth=net_worth,
        currency=currency
    )
```

### API Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT
- `GET /api/auth/me` - Get current user

**Transactions:**
- `GET /api/transactions` - List transactions
  - Query params: `?type=income&currency=GBP&category=Salary`
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/{id}` - Get single transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction
- `GET /api/transactions/summary` - Get summary
  - Query params: `?currency=GBP&year=2024&month=12`
- `GET /api/transactions/history` - Monthly history
  - Query params: `?months=6&currency=GBP`
- `GET /api/transactions/recurring` - Recurring transactions
  - Query params: `?currency=GBP`
- `POST /api/transactions/import` - Import CSV
- `GET /api/transactions/export` - Export CSV

**Entities:**
- `POST /api/entities` - Create entity
- `GET /api/entities/my-entity` - Get user's entity
- `GET /api/entities/{id}/summary` - Entity summary
  - Query params: `?currency=GBP`
- `POST /api/entities/{id}/invite` - Invite member
- `DELETE /api/entities/{id}/members/{user_id}` - Remove member

**Categories:**
- `GET /api/categories` - List categories
  - Query params: `?type=income&type=expense&type=asset&type=liability`
- `POST /api/categories` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

**Budgets:**
- `GET /api/budgets` - List budgets
- `POST /api/budgets` - Create budget
- `GET /api/budgets/progress` - Budget progress

### Technology Stack Details

### Backend
- **FastAPI** (Python 3.11+) - High-performance async web framework
- **Motor** - Asynchronous MongoDB driver
- **PyJWT** - JWT token handling
- **Pydantic** - Data validation
- **Bcrypt** - Password hashing

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Data visualization
- **Axios** - HTTP client
- **React Router** - Client-side routing

### Database
- **MongoDB 7.0+** - NoSQL database with indexing
- **Collections**: users, transactions, entities, categories, budgets

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Production static file serving

---

## 💱 Multi-Currency Support

### Supported Currencies (27+)

| Region | Currencies |
|--------|-----------|
| **Americas** | USD, CAD, MXN, BRL |
| **Europe** | EUR, GBP, CHF, SEK, NOK, PLN |
| **Asia-Pacific** | INR, JPY, CNY, HKD, SGD, AUD, NZD, KRW, THB, MYR, IDR, PHP |
| **Middle East & Africa** | AED, ZAR |
| **Emerging Markets** | RUB, TRY |

### Setting Up Multi-Currency

```
1. Go to Settings
2. Active Currencies → Select multiple currencies (e.g., GBP, USD, INR, EUR)
3. Primary Currency → Choose your main currency (e.g., GBP)
4. Save Settings
```

### Currency Features

#### Individual Dashboard
- **Multi-Currency View**: Shows all currencies in separate cards
- **Single Currency View**: Focus on one currency with dropdown selector
- **Currency Tabs**: Switch between currencies in Income/Expense/Asset/Liability screens
- **Primary Currency**: Auto-selected first in all tabs

#### Entity Dashboard
- **Currency Selector**: Dropdown to view entity finances by currency
- **Shared Transactions**: Filtered by selected currency
- **Member Breakdown**: Per-currency for admins

#### Forecast View
- **Currency Dropdown**: Select any currency for forecast
- **Currency-Specific Projections**: Separate forecasts for each currency
- **Recurring Transactions**: Filtered by selected currency

### Currency Tab Behavior

**Example: User selects GBP (primary), INR, USD**

```
Income Screen Tabs:  [GBP] | INR | USD
                       ↑
                 Auto-selected, always first

Click INR → View INR income transactions
Click USD → View USD income transactions
```

### Net Worth by Currency

**Multi-Currency Dashboard**:
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    GBP      │  │    INR      │  │    USD      │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ Net Worth   │  │ Net Worth   │  │ Net Worth   │
│  £9,100     │  │ ₹125,000    │  │  $15,000    │
│ Balance +   │  │ Balance +   │  │ Balance +   │
│ Net Assets  │  │ Net Assets  │  │ Net Assets  │
└─────────────┘  └─────────────┘  └─────────────┘
```

**Single Currency View** (GBP):
```
┌────────────────────────────────────────────────┐
│ 🏆 Current Net Worth (GBP)  Calculation:      │
│    £9,100                    (£2,500 - £1,200)│
│ Balance £1,300 + Assets      +                │
│ £7,800                       (£10,000 - £2,200)│
│                              = £9,100         │
└────────────────────────────────────────────────┘
```

---

## 👥 Entity Management

### What are Entities?

Entities are collaborative groups (households, offices, or custom groups) where members can share financial data while maintaining individual privacy.

### Entity Types

| Type | Icon | Description | Example Use Case |
|------|------|-------------|------------------|
| **Home** | 🏠 | Family/Household | Track family budget, shared expenses |
| **Office** | 💼 | Workplace/Team | Manage team expenses, project budgets |
| **Custom** | 🎨 | Any other group | Clubs, roommates, business partners |

### User Roles

#### 👤 Member Role
**Capabilities:**
- ✅ View shared transactions from all members
- ✅ Add own transactions (shared or private)
- ✅ View entity financial summary (shared data only)
- ✅ Leave entity at any time

**Restrictions:**
- ❌ Cannot see private transactions of other members
- ❌ Cannot see per-member breakdown
- ❌ Cannot invite or remove members

#### 👑 Admin Role
**Full Member Capabilities Plus:**
- ✅ View ALL transactions (shared AND private)
- ✅ See detailed per-member breakdown
- ✅ Toggle between "Shared Only" and "All Transactions" views
- ✅ Invite and remove members
- ✅ Promote/demote members
- ✅ Update entity settings

### Creating and Managing Entities

```typescript
// Create Entity
Entity → Create Entity
  ├─ Name: "Smith Family"
  ├─ Type: Home | Office | Custom
  └─ Description: "Family finances"

// Invite Members (Admin only)
Entity → Management → Invite Member
  ├─ Email: member@example.com
  └─ Role: Admin | Member

// Entity Dashboard with Currency Selection
Entity → Currency: [GBP ▼]
  ├─ Select GBP → View GBP transactions
  ├─ Select USD → View USD transactions
  └─ All views respect selected currency
```

---

## 📊 Asset & Liability Tracking

### Asset Management

**Default Asset Categories:**
- 💵 **Cash** - Bank accounts, savings, cash on hand
- 📈 **Investments** - Stocks, bonds, mutual funds, retirement accounts
- 🏠 **Property** - Real estate, land, vehicles
- 💎 **Valuables** - Jewelry, art, collectibles

**Features:**
- ✅ Multi-currency support (separate tabs per currency)
- ✅ Category-based organization
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Included in Net Worth calculations

### Liability Management

**Default Liability Categories:**
- 🏠 **Mortgages** - Home loans, property mortgages
- 💳 **Loans** - Personal loans, car loans, student loans
- 💳 **Credit Cards** - Credit card debt

**Features:**
- ✅ Multi-currency support
- ✅ Track outstanding balances
- ✅ Full CRUD operations
- ✅ Deducted from Net Worth

### Adding Assets/Liabilities

```
Assets → Add Asset
  ├─ Currency: [GBP] (auto-selected primary)
  ├─ Description: "Savings Account"
  ├─ Amount: 10,000
  ├─ Category: Cash
  └─ Date: 2024-01-01

Liabilities → Add Liability
  ├─ Currency: [GBP]
  ├─ Description: "Home Mortgage"
  ├─ Amount: 200,000
  ├─ Category: Mortgages
  └─ Date: 2024-01-01
```

---

## 🔮 Financial Forecasting

### Overview

The Forecast feature predicts your financial future for the next 6 months based on:
- Current balance (Income - Expenses)
- Historical transaction patterns (last 6 months)
- Recurring monthly transactions (salary, rent, subscriptions, etc.)

### Three Scenarios

| Scenario | Description | Calculation |
|----------|-------------|-------------|
| **Optimistic** | Best case | Income +5%, Expenses -5% |
| **Base** | Most likely | Income/Expenses as-is |
| **Pessimistic** | Worst case | Income -5%, Expenses +5% |

### How It Works

```
1. Current Balance: £1,300
   (Income £2,500 - Expense £1,200)

2. Recurring Transactions:
   - Salary: £2,500/month (income)
   - Rent: £1,200/month (expense)

3. 6-Month Projection:
   Month 1: £2,600 (£1,300 + £2,500 - £1,200)
   Month 2: £3,900 (£2,600 + £1,300)
   Month 3: £5,200 (£3,900 + £1,300)
   Month 4: £6,500 (£5,200 + £1,300)
   Month 5: £7,800 (£6,500 + £1,300)
   Month 6: £9,100 (£7,800 + £1,300)

4. Net Worth Growth: £1,300 → £9,100 (+£7,800)
```

### Currency-Specific Forecasting

**Individual Dashboard:**
```
Dashboard → Forecast → Currency: [GBP ▼]
  ├─ View GBP forecast
  ├─ Switch to INR
  └─ View INR forecast (different projections)
```

**Entity Dashboard:**
```
Entity → Forecast → Currency: [GBP ▼]
  ├─ View entity GBP forecast
  └─ Switch currencies to see different projections
```

### Forecast Controls

- **Forecast Until**: Select target month (up to 12 months ahead)
- **History Window**: 3, 6, 9, or 12 months of historical data
- **Income/Expense Change**: Adjust optimistic/pessimistic percentage
- **Deviation Period**: Monthly or Yearly rate

### Visual Output

- **Line Chart**: Three colored lines showing scenarios over time
- **Assumptions Box**: Current baseline income/expense
- **Monthly Breakdown Table**: Detailed month-by-month projections

---

## 💰 Net Worth Dashboard

### What is Net Worth?

```
Net Worth = Cash Balance + Net Assets
          = (Income - Expenses) + (Assets - Liabilities)
```

### Dashboard Display

#### Multi-Currency View
Each currency card shows:
```
┌─────────────┐
│    GBP      │
├─────────────┤
│ Net Worth   │
│  £9,100     │ ← (£2,500 - £1,200) + (£10,000 - £2,200)
│ Balance +   │
│ Net Assets  │
└─────────────┘
```

#### Single Currency View
Large banner at top:
```
┌──────────────────────────────────────────────────────┐
│ 🏆 Current Net Worth (GBP)    Calculation:           │
│    £9,100                      (£2,500 - £1,200)     │
│                                +                     │
│    Balance £1,300 +            (£10,000 - £2,200)    │
│    Net Assets £7,800           = £9,100              │
└──────────────────────────────────────────────────────┘

Main Stats:
  ├─ Cash Balance: £1,300 (Income - Expenses)
  ├─ Total Income: £2,500
  └─ Total Expenses: £1,200

Financial Breakdown:
  ├─ Assets: £10,000
  ├─ Liabilities: £2,200
  ├─ Balance: £1,300
  └─ Net Assets: £7,800

💡 Net Worth Calculation:
Net Worth = Cash Balance + Net Assets
          = (Income - Expenses) + (Assets - Liabilities)
          = (£2,500 - £1,200) + (£10,000 - £2,200)
          = £9,100
```

### Accessing Net Worth Screen

```
Navigation → Net Worth
  ├─ View consolidated Net Worth
  ├─ See all currencies together
  └─ Detailed breakdown per currency
```

---

## 📡 API Documentation

### Interactive API Docs

**Swagger UI**: http://localhost:8002/docs (when running)

All endpoints except `/health`, `/api/auth/register`, and `/api/auth/login` require:
```
Authorization: Bearer <jwt_token>
```

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT
- `GET /api/auth/me` - Get current user

#### Transactions
- `GET /api/transactions` - List transactions (with currency filter)
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/summary` - Financial summary (with currency filter)
- `GET /api/transactions/history` - Monthly history (with currency filter)
- `GET /api/transactions/recurring` - Recurring transactions (with currency filter)

#### Entities
- `POST /api/entities` - Create entity
- `GET /api/entities/{id}/summary` - Entity summary (with currency filter)
- `GET /api/entities/{id}/history` - Entity history (with currency filter)
- `POST /api/entities/{id}/invite` - Invite member (admin only)

#### Categories
- `GET /api/categories` - List categories (filterable by type)
- `POST /api/categories` - Create custom category

#### Budgets
- `GET /api/budgets` - List budgets
- `POST /api/budgets` - Create budget
- `GET /api/budgets/progress` - Budget progress

---

## 🚀 Deployment

### Production Deployment with Docker

```bash
# 1. Update environment for production
cp .env.example .env.production
# Edit .env.production:
# - Set strong SECRET_KEY
# - Update MONGODB_URL (use MongoDB Atlas recommended)
# - Set CORS_ORIGINS to your domain

# 2. Build and start
docker-compose -f docker-compose.prod.yml up --build -d

# 3. Setup SSL (Let's Encrypt)
sudo certbot certonly --standalone -d yourdomain.com

# 4. Configure Nginx with SSL (see documentation)
```

### Environment Variables

**Required:**
- `MONGODB_URL` - MongoDB connection string
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `FRONTEND_URL` - CORS origin

**Optional:**
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token lifetime (default: 1440)
- `ENVIRONMENT` - development | production

---

## 🔧 Troubleshooting

### Common Issues

#### Application not loading
```bash
# Check if services are running
docker ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart
```

#### Dashboard shows zero/blank
```bash
# Check currency is set in settings
# Verify transactions have currency field
# Clear browser cache: Ctrl+Shift+R
```

#### Forecast shows flat line
```bash
# Ensure transactions are marked as recurring
# Check transactions have currency field
# Verify historical data exists (last 6 months)
# Clear browser cache
```

#### Net Worth not visible (light theme)
```bash
# Update to latest version (v2.1+)
# Uses fixed blue gradient (theme-independent)
# Clear browser cache: Ctrl+Shift+R
```

#### MongoDB connection error
```bash
# Check MongoDB is running
mongosh --eval "db.runCommand({ ping: 1 })"

# Verify MONGODB_URL in .env
# Restart MongoDB service
```

### Getting Help

1. **Check logs**: Backend/Frontend terminal output
2. **Verify configuration**: `.env` file settings
3. **Test API**: http://localhost:8002/docs
4. **Clear cache**: Browser hard refresh (Ctrl+Shift+R)

---

## 📜 Recent Changes

### v2.1.0 (January 2025)

**Multi-Currency Support:**
- ✅ Added 27+ currency support
- ✅ Currency tabs in all transaction screens
- ✅ Multi-currency and single-currency dashboard views
- ✅ Currency selector in forecast view
- ✅ Primary currency auto-selection

**Asset & Liability Tracking:**
- ✅ New Assets and Liabilities screens
- ✅ Default categories for both
- ✅ Multi-currency support for assets/liabilities
- ✅ Integrated into Net Worth calculations

**Enhanced Forecasting:**
- ✅ Currency-aware forecasting
- ✅ Fixed flat line issues
- ✅ Improved baseline calculation (uses recurring when sparse history)
- ✅ Currency selector for individual and entity forecasts

**Net Worth Enhancements:**
- ✅ Prominent Net Worth display in dashboard
- ✅ Detailed calculation breakdown
- ✅ Multi-currency Net Worth cards
- ✅ Theme-aware design (visible on all themes)

**Bug Fixes:**
- ✅ Fixed forecast baseline calculation with sparse data
- ✅ Fixed multi-currency dashboard blank cards
- ✅ Fixed Net Worth visibility in light themes
- ✅ Fixed recurring transaction detection
- ✅ Fixed currency filtering in all APIs

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using FastAPI, React, TypeScript, and MongoDB**

*Version 2.1.0 - Last Updated: January 2026*
