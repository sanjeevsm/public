# iTrack+ - Personal Finance Tracker

> A complete, production-ready personal finance tracker with multi-user collaboration, privacy controls, and real-time financial reporting.


[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]() [![Version](https://img.shields.io/badge/version-2.0.0-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]()

**Built with:** FastAPI • React • TypeScript • MongoDB • Docker

## 🎉 Complete CRUD Operations

This application includes **full CRUD (Create, Read, Update, Delete) functionality** for all major entities:

✅ **Entity Management** - Create, update, delete, and manage households/offices  
✅ **Income Tracking** - Add, edit, delete income with category filtering  
✅ **Expense Tracking** - Comprehensive expense management and reporting  
✅ **Category Management** - Custom categories with icons and colors  
✅ **Budget Management** - Set limits, track progress, receive alerts  
✅ **Member Management** - Invite, promote, demote, and remove members  

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture--tech-stack)
- [Project Structure](#-project-structure)
- [Entity Management](#-entity-management)
- [Privacy & Permissions](#-privacy--permissions)
- [User Workflows](#-user-workflows)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🚀 Features

### Core Features

#### 💰 Personal Finance Tracking
- ✅ Track income and expenses with detailed categorization
- ✅ Real-time balance calculations and financial summaries
- ✅ Category-based analytics and breakdown
- ✅ Date-based transaction history
- ✅ CSV import/export for data portability
- ✅ Visual charts and graphs (Chart.js integration)

#### 👥 Multi-User Collaboration (Entity Management)
- ✅ **Create Entities**: Households, Offices, or Custom groups
- ✅ **Invite Members**: Add family members, team members, or collaborators
- ✅ **Role-Based Access**: Admin (full control) vs Member (limited access)
- ✅ **Shared Transactions**: Visible to all entity members
- ✅ **Private Transactions**: Visible only to creator and admins
- ✅ **Entity Dashboard**: Real-time financial overview for the group
- ✅ **Member Management**: Invite, remove, promote, or demote members

#### 🔒 Privacy & Security
- ✅ **Transaction Privacy Modes**:
  - 🔒 **Private**: Only you and entity admins can see
  - 👥 **Shared**: All entity members can see
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **HTTP-only Cookies**: XSS protection
- ✅ **Password Hashing**: Bcrypt encryption
- ✅ **CORS Protection**: Configurable origins

#### 📊 Advanced Reporting (Admin Only)
- ✅ **Per-Member Breakdown**: See who spent/earned what
- ✅ **Shared vs All Comparison**: Compare shared vs total finances
- ✅ **Admin Toggle**: Switch between shared-only and all data views
- ✅ **Financial Oversight**: Full visibility for household/team leaders

#### 🎨 User Experience
- ✅ **Responsive Design**: Mobile, tablet, and desktop optimized
- ✅ **Modern UI**: Tailwind CSS with clean, intuitive interface
- ✅ **Real-time Updates**: Instant feedback on all actions
- ✅ **Loading States**: Clear indication of background operations
- ✅ **Error Handling**: User-friendly error messages
- ✅ **Entity Status Banner**: Dashboard widget for entity info

---

## 🔧 Admin & Theming (Recent)

### Superadmin provisioning
- A default **superadmin** user is automatically seeded on API startup to simplify initial setup.
- Default credentials (development only):
  - Username: `admin`
  - Email: `admin@example.com`
  - Password: `admin`
- The seeded user has `is_superadmin=true` and can perform global admin activities. For security, rotate or disable this account in production immediately.

### Admin API Endpoints
- `GET /api/admin/users` — list all users (superadmin-only)
- `PUT /api/admin/users/{user_id}` — update `entity_role`, `entity_id`, and `is_superadmin` for a user (superadmin-only). Example body: `{"entity_role":"admin","is_superadmin":true}`
- `DELETE /api/admin/users/{user_id}` — delete a user (superadmin-only; cannot delete yourself)

These endpoints are available to the superadmin for promotion/demotion and user management. Use the frontend admin UI at `/admin` for a simple user list and action buttons (read-only view by default).

### Theme support
- The frontend includes a theme selector (top-right in the navbar) with multiple options:
  - dark, light, midnight, forest, navy, warm
- Selection is persisted in `localStorage` and applied via the HTML `data-theme` attribute. You can extend theme tokens in `frontend/src/index.css` or the Tailwind config to customize colors.

---

#### 🐳 Production Ready
- ✅ **Dockerized**: Complete containerization for easy deployment
- ✅ **Docker Compose**: Multi-container orchestration
- ✅ **Environment Config**: Flexible configuration via .env
- ✅ **Nginx**: Production-ready static file serving
- ✅ **MongoDB**: Scalable NoSQL database with indexing

---

## ⚡ Quick Start

> **Choose Your Setup Method:**
> - **🐳 Docker Setup** (Recommended): Easiest setup with Docker
> - **🏠 Local Setup**: Run directly on your machine without Docker

### 📊 Quick Comparison

| Feature | Docker | Local |
|---------|--------|---------|
| **Setup Time** | 5 min | 15 min |
| **Startup Time** | 30-60 sec | 10-20 sec |
| **RAM Usage** | ~1.5GB | ~500MB |
| **Prerequisites** | Docker only | Python + Node + MongoDB |
| **Best For** | Production, Easy Setup | Development, Performance |
| **Updates** | Rebuild containers | Instant code changes |

### Docker Setup (Recommended)

#### Prerequisites

##### All Operating Systems
- 4GB RAM available
- 10GB free disk space
- Ports 3000, 8002, 27017 available

#### 🪟 Windows (10/11)
- **Docker Desktop for Windows** (20.10+) - [Download](https://docs.docker.com/desktop/install/windows-install/)
- **WSL 2** (Windows Subsystem for Linux) - Required for Docker Desktop
- **PowerShell 5.1+** or **Windows Terminal** (recommended)

#### 🐧 Linux (Ubuntu/Debian)
- **Docker Engine** (20.10+) - [Install Guide](https://docs.docker.com/engine/install/ubuntu/)
- **Docker Compose** (2.0+) - Usually included with Docker Engine
- **Bash** shell

#### 🍎 macOS (10.15+)
- **Docker Desktop for Mac** (20.10+) - [Download](https://docs.docker.com/desktop/install/mac-install/)
- **Bash** or **Zsh** shell
- **Homebrew** (optional, for local development)

---

### Platform Notes

- Windows users: Docker Desktop requires **WSL2** on modern Windows (10/11). Use PowerShell for Windows-specific examples shown in this README. When following POSIX examples, run them from WSL or Git Bash.
- macOS / Linux users: use the shell (`bash`/`zsh`) examples. Paths shown in Windows examples (e.g. `C:\data\db`) are illustrative — replace with POSIX paths (e.g. `/data/db`).
- Avoid committing virtual environments (`.venv/`, `venv/`) to the repository. Use the provided `.gitignore` entries and create venvs locally with `python -m venv .venv` per-project.
- If you run Docker on Windows via WSL2, prefer running build/start commands from a WSL shell to avoid path translation issues.


### 📝 Script Summary

iTrack+ includes convenient startup/stop scripts for both methods (now located under `scripts/`):

#### Windows (PowerShell)
```powershell
# Docker Method
.\scripts\verify.ps1         # Verify Docker installation
.\scripts\start.ps1          # Start with Docker
.\scripts\stop.ps1           # Stop Docker containers

# Local Method
.\scripts\setup-local.ps1    # One-time setup (first time only)
.\scripts\start-local.ps1    # Start application
.\scripts\stop-local.ps1     # Stop application
```

#### Linux/macOS (Bash)
```bash
# Docker Method
./scripts/verify.sh          # Verify Docker installation
./scripts/start.sh           # Start with Docker
./scripts/stop.sh            # Stop Docker containers

# Local Method
./scripts/setup-local.sh     # One-time setup (first time only)
./scripts/start-local.sh     # Start application
./scripts/stop-local.sh      # Stop application
```

---

### Installation by Operating System

#### 🪟 Windows Installation

**Step 1: Install Docker Desktop**
```powershell
# Download and install Docker Desktop for Windows
# https://docs.docker.com/desktop/install/windows-install/

# After installation, verify:
docker --version
docker-compose --version
```

**Step 2: Enable WSL 2**
```powershell
# Open PowerShell as Administrator
wsl --install

# Restart computer if prompted
# Set WSL 2 as default
wsl --set-default-version 2
```

# Step 2: Clone and Setup
```bash
# Navigate to project
cd public/workspace/python/itrack

# Create environment file
cp .env.example .env

# Make scripts executable
chmod +x scripts/start.sh scripts/verify.sh

# Verify installation
./scripts/verify.sh

# Start application
./scripts/start.sh
```
docker-compose up --build
```

---

#### 🐧 Linux Installation (Ubuntu/Debian)

**Step 1: Install Docker**
```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

# Step 2: Clone and Setup
```bash
# Navigate to project
cd public/workspace/python/itrack

# Create environment file
cp .env.example .env

# Make scripts executable
chmod +x scripts/start.sh scripts/verify.sh

# Verify installation
./scripts/verify.sh

# Start application
./scripts/start.sh
```

**Alternative - Manual Start (Linux):**
```bash
docker compose up --build
```

---

#### 🍎 macOS Installation

**Step 1: Install Docker Desktop**
```bash
# Option 1: Download from website
# https://docs.docker.com/desktop/install/mac-install/

# Option 2: Install via Homebrew
brew install --cask docker

# Start Docker Desktop from Applications
# Verify installation
docker --version
docker-compose --version
```

**Step 2: Clone and Setup**
```bash
# Navigate to project
cd public/workspace/python/itrack

# Create environment file
cp .env.example .env

# Make scripts executable
chmod +x scripts/start.sh scripts/verify.sh

# Verify installation
./scripts/verify.sh

# Start application
./scripts/start.sh
```

**Alternative - Manual Start (macOS):**
```bash
docker-compose up --build
```

---

### Quick Start Scripts

iTrack+ includes OS-specific scripts for easy setup:

### Windows
```powershell
# Verify installation
.\scripts\verify.ps1

# Start application
.\scripts\start.ps1

# Stop application
.\scripts\stop.ps1
```

### Linux/macOS
```bash
# Verify installation
./scripts/verify.sh

# Start application
./scripts/start.sh

# Stop application
./scripts/stop.sh
``` 

### Manual Start (All OS)

```bash
# Step 1: Navigate to project
cd public/workspace/python/itrack

# Step 2: Create environment file
cp .env.example .env  # Linux/macOS
Copy-Item .env.example .env  # Windows PowerShell

# Step 3: Start with Docker Compose
docker-compose up --build
```

Wait 30-60 seconds for all services to initialize.

---

### 🏠 Local Setup (No Docker Required)

> **Perfect for:** Development, no Docker available, or prefer native installation

#### Prerequisites

**1. Python 3.11+**
- **Windows**: [Download from python.org](https://www.python.org/downloads/) (⚠️ Check "Add Python to PATH")
- **Linux**: `sudo apt install python3 python3-pip python3-venv`
- **macOS**: `brew install python@3.11`

**2. Node.js 16+**
- **Windows**: [Download from nodejs.org](https://nodejs.org/)
- **Linux**: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install nodejs`
- **macOS**: `brew install node`

**3. MongoDB 7.0+** (Choose one)

#### Quick Start Scripts

**Windows (PowerShell):**
```powershell
# 1. Setup (first time only)
.\setup-local.ps1

# 2. Start application
.\start-local.ps1

# 3. Stop application
.\stop-local.ps1
```

**Linux/macOS (Bash):**
```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# 1. Setup (first time only)
./setup-local.sh

# 2. Start application
./start-local.sh

# 3. Stop application
./stop-local.sh
```

#### What the Setup Does

The `setup-local` script will:
1. ✅ Verify Python 3.11+ is installed
2. ✅ Verify Node.js 16+ is installed
3. ✅ Check MongoDB availability
4. ✅ Create Python virtual environment
5. ✅ Install backend dependencies (FastAPI, Motor, etc.)
6. ✅ Install frontend dependencies (React, Vite, etc.)
7. ✅ Create `.env` configuration files
8. ✅ Configure MongoDB connection

#### MongoDB Setup Options

**Option A: Local MongoDB Installation**

**Windows:**
```powershell
# Download installer from https://www.mongodb.com/try/download/community
# OR use Chocolatey:
choco install mongodb

# Start MongoDB service:
net start MongoDB

# Stop MongoDB service:
net stop MongoDB
```

**Linux (Ubuntu/Debian):**
```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB:
sudo systemctl start mongod
sudo systemctl enable mongod

# Check status:
sudo systemctl status mongod
```

**macOS:**
```bash
# Install via Homebrew:
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB:
brew services start mongodb-community

# Stop MongoDB:
brew services stop mongodb-community
```

**Option B: MongoDB Atlas (Cloud - Free Tier)**

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free M0 cluster (512MB storage)
3. Configure Network Access (add IP: 0.0.0.0/0 for development)
4. Create Database User (username + password)
5. Get connection string from "Connect" button
6. Update `.env` file:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/itrack_db?retryWrites=true&w=majority
   ```

**Advantages:**
- **Local**: No internet required, full control, faster, free
- **Atlas**: No installation, automatic backups, accessible anywhere

#### Manual Installation (Without Scripts)

**Step 1: Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Step 2: Setup Frontend**
```bash
cd frontend

# Install dependencies
npm install
```

**Step 3: Configure Environment**
```bash
# Copy environment template
cp .env.example .env  # Linux/macOS
Copy-Item .env.example .env  # Windows

# Edit .env file and update:
# - MONGODB_URL=mongodb://localhost:27017 (or Atlas connection string)
# - SECRET_KEY=your-secret-key-change-in-production

# Create frontend .env
echo "VITE_API_URL=http://localhost:8002" > frontend/.env
```

**Step 4: Start Services**
```bash
# Terminal 1: Start MongoDB (if not running as service)
mongod --dbpath /data/db  # Linux/macOS
mongod --dbpath C:\data\db  # Windows

# Terminal 2: Start Backend
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 3: Start Frontend
cd frontend
npm run dev
```

#### Advantages of Local Setup

✅ **Faster Startup**: 10-20 seconds vs 30-60 seconds with Docker  
✅ **Lower Resource Usage**: Native processes use less RAM  
✅ **Better for Development**: Instant code changes, no rebuilds  
✅ **Direct Debugging**: Easier to debug and inspect  
✅ **Flexible**: Use your preferred MongoDB (local or cloud)  

#### Disadvantages

❌ **More Setup**: Requires installing Python, Node.js, and MongoDB  
❌ **OS-Specific**: Different commands for Windows/Linux/macOS  
❌ **Manual Dependencies**: Must manage Python/Node versions  

---

### Step 4: Access Application

```
Frontend:  http://localhost:3000
Backend:   http://localhost:8002
API Docs:  http://localhost:8002/docs
```

### Step 5: Create Your Account

1. Open http://localhost:3000
2. Click "Register"
3. Enter your details:
   - Username: Your Name
   - Email: your@email.com
   - Password: YourSecurePassword123!
4. Click "Register"
5. You're in! Start tracking finances.

### First Steps

**Add Your First Transaction:**
```
Dashboard → Add Transaction
  ├─ Description: "Monthly Salary"
  ├─ Amount: 5000
  ├─ Type: Income
  ├─ Category: Salary
  └─ Click "Add Transaction"
```

**Create an Entity (Optional):**
```
Entity → Create Entity
  ├─ Name: "Smith Family"
  ├─ Type: Home
  ├─ Description: "Family finances"
  └─ Click "Create Entity"
```

**Invite Family Members (Optional):**
```
Entity → Management Tab → Invite Member
  ├─ Email: john@example.com
  ├─ Role: Member (or Admin)
  └─ Click "Send Invitation"
```

---

## 🏗️ Architecture & Tech Stack

### Backend
- **FastAPI** (Python 3.11+) - High-performance async web framework
- **Motor** - Asynchronous MongoDB driver
- **PyJWT** - JWT token handling
- **Pydantic** - Data validation

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Data visualization
- **Axios** - HTTP client

### Database
- **MongoDB** - NoSQL database with indexing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Production-ready static file serving

## 📁 Project Structure

```
itrack/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── users.py             # User management
│   │   │   ├── transactions.py      # Transaction CRUD
│   │   │   └── entities.py          # Entity management ⭐ NEW
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # App configuration
│   │   │   ├── security.py          # JWT & password hashing
│   │   │   └── database.py          # MongoDB connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User Pydantic models
│   │   │   ├── transaction.py       # Transaction models
│   │   │   └── entity.py            # Entity models ⭐ NEW
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # Auth business logic
│   │   │   ├── transaction_service.py # Transaction logic
│   │   │   └── entity_service.py    # Entity logic ⭐ NEW
│   │   └── main.py                  # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CategoryChart.tsx
│   │   │   ├── DashboardSummary.tsx
│   │   │   ├── EntityCreateForm.tsx       # ⭐ NEW
│   │   │   ├── EntityDashboardSummary.tsx # ⭐ NEW
│   │   │   ├── EntityManagement.tsx       # ⭐ NEW
│   │   │   ├── EntityStatusBanner.tsx     # ⭐ NEW
│   │   │   ├── ImportExport.tsx
│   │   │   ├── Navbar.tsx                 # Updated
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── TransactionForm.tsx        # Updated
│   │   │   └── TransactionList.tsx        # Updated
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx            # Updated
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx          # Updated
│   │   │   ├── EntityPage.tsx             # ⭐ NEW
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── authService.ts
│   │   │   ├── entityService.ts           # ⭐ NEW
│   │   │   └── transactionService.ts
│   │   ├── types/
│   │   │   ├── entity.ts                  # ⭐ NEW
│   │   │   ├── transaction.ts             # Updated
│   │   │   └── user.ts
│   │   ├── App.tsx                        # Updated
│   │   ├── main.tsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
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

#### 🔵 Member Role

**Capabilities:**
- ✅ View shared transactions from all members
- ✅ Add their own transactions (shared or private)
- ✅ View entity financial summary (shared data only)
- ✅ See list of entity members
- ✅ Leave entity at any time

**Restrictions:**
- ❌ Cannot see private transactions of other members
- ❌ Cannot see per-member breakdown
- ❌ Cannot invite new members
- ❌ Cannot remove members
- ❌ Cannot change member roles
- ❌ Cannot update entity settings

#### 👑 Admin Role

**Full Member Capabilities Plus:**
- ✅ View ALL transactions (shared AND private)
- ✅ See detailed per-member breakdown (income/expense/balance)
- ✅ Toggle between "Shared Only" and "All Transactions" views
- ✅ Invite new members to the entity
- ✅ Remove members from the entity
- ✅ Promote members to admin or demote to member
- ✅ Update entity settings (name, description)
- ✅ Full financial oversight and accountability

**Purpose:** Admins are typically household heads, team leaders, or group organizers who need full visibility for oversight.

### Creating an Entity

```typescript
// Navigation: Entity → Create Entity

Form Fields:
  ├─ Entity Name: "Smith Family" (required)
  ├─ Entity Type: Home | Office | Custom (required)
  ├─ Custom Type Name: "Club" (if Custom selected)
  └─ Description: "Family household finances" (optional)

Result:
  ├─ Entity created successfully
  ├─ You become the admin (creator)
  └─ Can now invite members
```

### Inviting Members

```typescript
// Navigation: Entity → Management Tab → Invite Member
// Permission: Admin only

Form Fields:
  ├─ Email: member@example.com (must have existing account)
  └─ Role: Admin | Member

Result:
  ├─ Member added to entity immediately
  ├─ Member sees entity in their account
  └─ Member can access entity dashboard

Note: Users must register first before they can be invited.
```

### Transaction Privacy Modes

#### 🔒 Private Mode (Default)

**Visibility:**
- ✅ Transaction creator can see
- ✅ Entity admins can see
- ❌ Other entity members CANNOT see

**Use Cases:**
- Personal purchases
- Individual income
- Private expenses
- Gifts or surprises

**Example:**
```
"Birthday gift for spouse" - $50 - Private
→ Only you and admins see this
→ Spouse (if member) does NOT see it
```

#### 👥 Shared Mode

**Visibility:**
- ✅ ALL entity members can see
- ✅ Included in entity summary
- ✅ Visible in entity transaction list

**Use Cases:**
- Household bills
- Shared groceries
- Team expenses
- Common purchases

**Example:**
```
"Monthly electricity bill" - $120 - Shared
→ All family members can see this
→ Included in family budget overview
```

### Entity Dashboard Views

#### Member View (Shared Only)

```
┌──────────────────────────────────────┐
│  👤 Member View                      │
│  🔓 Shared Only                      │
├──────────────────────────────────────┤
│  Total Balance:    $4,800            │
│  Total Income:     $5,000            │
│  Total Expense:    $200              │
├──────────────────────────────────────┤
│  Shared Transactions: 15             │
│  Category Breakdown: [chart]         │
└──────────────────────────────────────┘
```

#### Admin View (Shared Only)

```
┌──────────────────────────────────────┐
│  👑 Admin View                       │
│  🔓 Shared Only                      │
├──────────────────────────────────────┤
│  [Same as Member View]               │
│  + Toggle to view ALL transactions   │
└──────────────────────────────────────┘
```

#### Admin View (All Transactions)

```
┌──────────────────────────────────────┐
│  👑 Admin View                       │
│  🔐 All Transactions                 │
├──────────────────────────────────────┤
│  Total Balance:    $4,500            │
│  Total Income:     $5,000            │
│  Total Expense:    $500              │
├──────────────────────────────────────┤
│  Shared vs All Comparison:           │
│  Shared:  $4,800 | All: $4,500       │
├──────────────────────────────────────┤
│  Per-Member Breakdown:               │
│  Dad:   $4,700 ($5,000 - $300)       │
│  Mom:   -$150  ($0 - $150)           │
│  Son:   -$50   ($0 - $50)            │
├──────────────────────────────────────┤
│  Transaction Counts:                 │
│  Total: 25 | Shared: 15 | Private: 10│
└──────────────────────────────────────┘
```

### Managing Members

#### View Members
```
Entity → Management Tab
  └─ Shows list of all members with:
     ├─ Username
     ├─ Role (Admin 👑 / Member 👤)
     ├─ Joined date
     └─ Actions (admin only)
```

#### Remove Member (Admin)
```
Entity → Management → Click 🗑️ Remove
  ├─ Confirmation dialog appears
  ├─ Member removed from entity
  └─ Member loses access to entity data
```

#### Change Role (Admin)
```
Entity → Management → Click ⬆️ Promote / ⬇️ Demote
  ├─ Promote: Member → Admin (full access)
  └─ Demote: Admin → Member (limited access)

Note: Cannot demote yourself if you're the only admin
```

#### Leave Entity
```
Entity → Management → Leave Entity (bottom)
  ├─ Available to all members
  ├─ Confirmation required
  ├─ Lose access to entity data
  └─ Can be invited back later

Note: Admins warned if they're the only admin
```

---

## 🔐 Privacy & Permissions

### Transaction Visibility Matrix

| Role | Own Private | Own Shared | Member Private | Member Shared |
|------|-------------|------------|----------------|---------------|
| **Member** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Admin**  | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Non-Member** | ❌ No | ❌ No | ❌ No | ❌ No |

### Privacy Design Philosophy

1. **Private by Default** 🔒
   - All transactions default to private mode
   - Users must explicitly choose to share
   - Safest option for personal data

2. **Explicit Sharing** 👥
   - Users opt-in to sharing each transaction
   - Clear visual indicators (radio buttons)
   - Cannot accidentally share

3. **Admin Oversight** 👑
   - Admins have full visibility by design
   - Necessary for household/team management
   - Clear indication when admin views all data

4. **Member Privacy** 🛡️
   - Members cannot see each other's private data
   - Shared transactions visible to all
   - Balance between collaboration and privacy

### Security Features

#### Authentication
- ✅ JWT (JSON Web Tokens) for stateless auth
- ✅ HTTP-only cookies (XSS protection)
- ✅ Password hashing with bcrypt
- ✅ Secure token refresh mechanism
- ✅ Automatic token expiration

#### Authorization
- ✅ Role-based access control (RBAC)
- ✅ Endpoint-level permission checks
- ✅ Database query filtering by user
- ✅ Entity membership validation

#### Data Protection
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (NoSQL)
- ✅ Environment variable secrets

---

## 🎯 User Workflows

### Workflow 1: Personal Finance Tracking (Solo)

```
1. Register account
2. Login to dashboard
3. Add income transaction:
   ├─ "Monthly Salary" - $5,000 - Income
   └─ No entity needed
4. Add expense transactions:
   ├─ "Rent" - $1,200 - Expense
   ├─ "Groceries" - $300 - Expense
   └─ "Entertainment" - $100 - Expense
5. View personal summary:
   ├─ Balance: $3,400
   ├─ Income: $5,000
   └─ Expense: $1,600
6. Export monthly report (CSV)
```

### Workflow 2: Family Budget Management

```
1. Parent (Dad) creates "Smith Family" entity (Type: Home)
2. Dad invites Mom (Admin) and Kids (Members)
3. Everyone adds transactions:
   ├─ Dad: "Salary" - $5,000 - Income - Shared
   ├─ Mom: "Freelance" - $2,000 - Income - Shared
   ├─ Dad: "Personal gift" - $100 - Expense - Private
   ├─ Mom: "Groceries" - $300 - Expense - Shared
   ├─ Son: "School supplies" - $50 - Expense - Shared
   └─ Daughter: "Personal item" - $30 - Expense - Private
4. Kids view entity dashboard:
   ├─ See shared income ($7,000)
   ├─ See shared expenses ($350)
   └─ Cannot see parents' private transactions
5. Parents toggle "All Transactions" view:
   ├─ See all family transactions
   ├─ Per-member breakdown:
   │   ├─ Dad: +$4,900 ($5,000 - $100)
   │   ├─ Mom: +$1,700 ($2,000 - $300)
   │   ├─ Son: -$50
   │   └─ Daughter: -$30
   └─ Full financial picture
```

### Workflow 3: Team Expense Tracking

```
1. Team Lead creates "Marketing Team" entity (Type: Office)
2. Lead invites team members as Members
3. Everyone logs expenses:
   ├─ Lead: "Client dinner" - $200 - Expense - Shared
   ├─ Member A: "Taxi to meeting" - $25 - Expense - Shared
   ├─ Member B: "Office supplies" - $75 - Expense - Shared
   └─ Lead: "Personal lunch" - $15 - Expense - Private
4. Team members see shared expenses only:
   ├─ Total: $300 (shared)
   └─ Cannot see lead's personal expenses
5. Team Lead reviews all expenses:
   ├─ Shared: $300
   ├─ Private: $15
   ├─ Total: $315
   └─ Prepares reimbursement report
```

### Workflow 4: Admin Financial Oversight

```
1. Admin logs into entity dashboard
2. Default view shows shared transactions only
3. Admin toggles "Include Private" switch ON
4. Dashboard updates to show:
   ├─ All transactions (shared + private)
   ├─ Comparison table:
   │   ├─ Shared Only: $4,800 balance
   │   └─ All Transactions: $4,500 balance
   ├─ Per-Member Breakdown:
   │   ├─ Member A: $2,000 income, $500 expense
   │   ├─ Member B: $1,000 income, $200 expense
   │   └─ Member C: $0 income, $300 expense
   └─ Full visibility for accountability
5. Admin exports comprehensive report
```

---

## 📡 API Reference

Interactive Swagger docs available at **http://localhost:8002/docs** when running.
All endpoints except `/`, `/health`, `POST /api/auth/register`, and `POST /api/auth/login` require `Authorization: Bearer <token>`.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive JWT |
| POST | `/api/auth/logout` | Revoke current token |
| GET | `/api/auth/me` | Get current user profile |

**Login request body:**
```json
{ "email": "user@example.com", "password": "yourpassword" }
```
**Login response:**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions` | List transactions (`skip`, `limit` 1–1000, `type`, `category`) |
| POST | `/api/transactions` | Create transaction |
| GET | `/api/transactions/{id}` | Get transaction |
| PUT | `/api/transactions/{id}` | Update transaction |
| DELETE | `/api/transactions/{id}` | Delete transaction |
| GET | `/api/transactions/summary` | Balance, income/expense totals + category breakdown |
| GET | `/api/transactions/export` | Download all transactions as CSV |
| POST | `/api/transactions/import` | Import transactions from CSV (max 5 MB) |

**Create/update body fields:** `description` (str), `amount` (float >0), `type` (income\|expense), `category` (str), `date` (ISO datetime), `mode` (shared\|private).

**CSV format:** `description,amount,type,category,date`

---

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List categories (`type` filter: income\|expense\|both) |
| POST | `/api/categories` | Create custom category |
| GET | `/api/categories/{id}` | Get category |
| PUT | `/api/categories/{id}` | Update custom category |
| DELETE | `/api/categories/{id}` | Delete custom category |
| GET | `/api/categories/stats` | Category usage statistics |

**Create body fields:** `name`, `type` (income\|expense\|both), `color` (`#RRGGBB`), `icon` (emoji), `description`.

---

### Budgets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/budgets` | List budgets (`active_only` bool) |
| POST | `/api/budgets` | Create budget |
| GET | `/api/budgets/{id}` | Get budget |
| PUT | `/api/budgets/{id}` | Update budget |
| DELETE | `/api/budgets/{id}` | Delete budget |
| GET | `/api/budgets/progress` | Progress for all active budgets |
| GET | `/api/budgets/{id}/progress` | Progress for one budget |
| GET | `/api/budgets/alerts` | Budgets at or over alert threshold |

**Create body fields:** `name`, `amount` (float >0), `period` (daily\|weekly\|monthly\|yearly), `budget_type` (category\|total), `category` (str, for category budgets), `start_date`, `end_date` (optional), `alert_threshold` (0–100, default 80).

---

### Entities

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/entities` | Create entity |
| GET | `/api/entities/my-entity` | Get current user's entity |
| GET | `/api/entities/{id}` | Get entity by ID (members only) |
| PUT | `/api/entities/{id}` | Update entity (admin only) |
| DELETE | `/api/entities/{id}` | Delete entity — clears all members & detaches transactions (admin only) |
| GET | `/api/entities/{id}/members` | List members with user details |
| POST | `/api/entities/{id}/invite` | Invite user by email (admin only) |
| DELETE | `/api/entities/{id}/members/{uid}` | Remove member (admin only) |
| PUT | `/api/entities/{id}/members/{uid}/role` | Change member role (admin only) |
| POST | `/api/entities/leave` | Leave current entity |
| GET | `/api/entities/{id}/summary` | Financial summary (`include_private` for admins) |

**Create body fields:** `name`, `entity_type` (Home\|Office\|Custom), `custom_type_name` (if Custom), `description`.

---

### Navigation Quick Reference

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/dashboard` | Balance overview, charts, recent transactions |
| Income | `/income` | Manage income transactions |
| Expenses | `/expenses` | Manage expense transactions |
| Categories | `/categories` | Create and manage categories |
| Budgets | `/budgets` | Set and track spending limits |
| Entity | `/entity` | Manage household/office entity |
| Members | `/members` | Manage entity members and roles |

---

## 📦 Database Schema

### Collections Overview

```
MongoDB Database: itrack
├── users           (User accounts)
├── transactions    (Financial transactions)
└── entities        (Collaborative groups)
```

### Users Collection

```javascript
{
  _id: ObjectId,
  username: string,               // Display name
  email: string,                  // Unique login email
  hashed_password: string,        // Bcrypt hashed
  entity_id: string | null,       // Current entity (optional)
  entity_role: "admin" | "member" | null,  // Role in entity
  created_at: datetime,
  updated_at: datetime
}

// Indexes:
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ entity_id: 1 });
```

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "username": "John Smith",
  "email": "john@example.com",
  "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU2jK...",
  "entity_id": "507f1f77bcf86cd799439022",
  "entity_role": "admin",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Transactions Collection

```javascript
{
  _id: ObjectId,
  user_id: string,                // Transaction owner
  description: string,            // Transaction description
  amount: float,                  // Transaction amount
  type: "income" | "expense",    // Transaction type
  category: string,               // Category name
  date: datetime,                 // Transaction date
  mode: "shared" | "private",    // Privacy mode (default: private)
  entity_id: string | null,       // Entity (if user in entity)
  created_at: datetime,
  updated_at: datetime
}

// Indexes:
db.transactions.createIndex({ user_id: 1, date: -1 });
db.transactions.createIndex({ entity_id: 1, mode: 1 });
db.transactions.createIndex({ type: 1 });
db.transactions.createIndex({ category: 1 });
```

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439033",
  "user_id": "507f1f77bcf86cd799439011",
  "description": "Monthly Salary",
  "amount": 5000.00,
  "type": "income",
  "category": "Salary",
  "date": "2024-01-31T00:00:00Z",
  "mode": "shared",
  "entity_id": "507f1f77bcf86cd799439022",
  "created_at": "2024-01-31T10:00:00Z",
  "updated_at": "2024-01-31T10:00:00Z"
}
```

### Entities Collection

```javascript
{
  _id: ObjectId,
  name: string,                   // Entity name
  entity_type: "Home" | "Office" | "Custom",
  custom_type_name: string | null,// Custom type name (if Custom)
  description: string | null,     // Optional description
  members: [
    {
      user_id: string,            // Member user ID
      role: "admin" | "member",   // Member role
      joined_at: datetime          // When joined
    }
  ],
  created_by: string,             // Creator user ID
  created_at: datetime,
  updated_at: datetime
}

// Indexes:
db.entities.createIndex({ "members.user_id": 1 });
db.entities.createIndex({ created_by: 1 });
```

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439022",
  "name": "Smith Family",
  "entity_type": "Home",
  "custom_type_name": null,
  "description": "Family household finances",
  "members": [
    {
      "user_id": "507f1f77bcf86cd799439011",
      "role": "admin",
      "joined_at": "2024-01-01T00:00:00Z"
    },
    {
      "user_id": "507f1f77bcf86cd799439012",
      "role": "member",
      "joined_at": "2024-01-05T00:00:00Z"
    }
  ],
  "created_by": "507f1f77bcf86cd799439011",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-05T00:00:00Z"
}
```

### Data Relationships

```
User (1) ─────── (N) Transaction
  │                         |
  │                    user_id
  │
  └─────── (0..1) Entity
                            |
                       entity_id
                            |
                       members[]

Entity (1) ─────── (N) Transaction
                            |
                       entity_id
```

---

## 🚀 Deployment

### Production Deployment with Docker

#### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Docker 20.10+
- Docker Compose 2.0+
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 2: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd itrack

# Create production environment file
cp .env.example .env.production
```

#### Step 3: Configure Production Environment

**Edit `.env.production`:**
```bash
# MongoDB
MONGODB_URL=mongodb://itrack_user:STRONG_PASSWORD@mongo:27017
DATABASE_NAME=itrack_prod

# Security (IMPORTANT: Change these!)
SECRET_KEY=<generate-64-char-random-string>
# Generate with: openssl rand -hex 32

# CORS (set your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Settings
API_V1_STR=/api
PROJECT_NAME=iTrack+
DEBUG=false

# Frontend
VITE_API_URL=https://yourdomain.com/api
```

#### Step 4: Create Production Docker Compose

**Create `docker-compose.prod.yml`:**
```yaml
version: '3.8'

services:
  mongo:
    image: mongo:6.0
    container_name: itrack-mongo-prod
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: itrack_user
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo-data-prod:/data/db
    networks:
      - itrack-network

  backend:
    build: ./backend
    container_name: itrack-backend-prod
    restart: always
    env_file:
      - .env.production
    depends_on:
      - mongo
    networks:
      - itrack-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: itrack-frontend-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - itrack-network

volumes:
  mongo-data-prod:

networks:
  itrack-network:
    driver: bridge
```

#### Step 5: SSL/TLS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Stop any running services
docker-compose down

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Set permissions
sudo chown -R $USER:$USER nginx/ssl
```

#### Step 6: Configure Nginx for Production

**Create `frontend/nginx.prod.conf`:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /usr/share/nginx/html;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Step 7: Deploy

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up --build -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify containers running
docker-compose -f docker-compose.prod.yml ps
```

#### Step 8: Setup Auto-Renewal for SSL

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab for auto-renewal
sudo crontab -e

# Add this line:
0 0 * * * certbot renew --quiet && docker-compose -f /path/to/itrack/docker-compose.prod.yml restart frontend
```

### Monitoring & Maintenance

#### Health Checks

```bash
# Backend health
curl https://yourdomain.com/api/health

# Check containers
docker ps

# Check resource usage
docker stats
```

#### Database Backup

```bash
# Backup MongoDB
docker exec itrack-mongo-prod mongodump --out=/backup
docker cp itrack-mongo-prod:/backup ./backup-$(date +%Y%m%d)

# Restore MongoDB
docker cp ./backup itrack-mongo-prod:/backup
docker exec itrack-mongo-prod mongorestore /backup
```

#### Log Management

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Clear logs
docker-compose -f docker-compose.prod.yml logs --tail=0 -f
```

### Scaling (Optional)

```bash
# Scale backend instances
docker-compose -f docker-compose.prod.yml up --scale backend=3 -d

# Add load balancer (Nginx upstream)
# Edit nginx.prod.conf
upstream backend {
  server backend:8002;
  server backend:8003;
  server backend:8004;
}
```

### Complete API Reference

**Base URL:** `http://localhost:8002/api`

**Interactive Docs:** `http://localhost:8002/docs` (Swagger UI)

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login user | No |
| POST | `/auth/logout` | Logout user | Yes |
| GET | `/auth/me` | Get current user info | Yes |

**Example: Register**
```bash
curl -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Example: Login**
```bash
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }' \
  -c cookies.txt
```

#### Transaction Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/transactions` | List all user transactions | Yes |
| POST | `/transactions` | Create new transaction | Yes |
| GET | `/transactions/{id}` | Get specific transaction | Yes |
| PUT | `/transactions/{id}` | Update transaction | Yes |
| DELETE | `/transactions/{id}` | Delete transaction | Yes |
| GET | `/transactions/summary` | Get financial summary | Yes |
| GET | `/transactions/export` | Export transactions to CSV | Yes |
| POST | `/transactions/import` | Import transactions from CSV | Yes |

**Example: Create Transaction**
```bash
curl -X POST http://localhost:8002/api/transactions \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "description": "Monthly Salary",
    "amount": 5000,
    "type": "income",
    "category": "Salary",
    "date": "2024-01-01T00:00:00Z",
    "mode": "private"
  }'
```

**Example: Get Summary**
```bash
curl -X GET http://localhost:8002/api/transactions/summary \
  -b cookies.txt
```

#### Entity Endpoints

| Method | Endpoint | Description | Auth Required | Permission |
|--------|----------|-------------|---------------|------------|
| POST | `/entities` | Create new entity | Yes | Any |
| GET | `/entities/my-entity` | Get user's entity | Yes | Any |
| GET | `/entities/{id}` | Get entity by ID | Yes | Member |
| PUT | `/entities/{id}` | Update entity settings | Yes | Admin |
| POST | `/entities/{id}/invite` | Invite member to entity | Yes | Admin |
| POST | `/entities/leave` | Leave current entity | Yes | Any |
| DELETE | `/entities/{id}/members/{user_id}` | Remove member | Yes | Admin |
| PUT | `/entities/{id}/members/{user_id}/role` | Change member role | Yes | Admin |
| GET | `/entities/{id}/members` | Get all entity members | Yes | Member |
| GET | `/entities/{id}/summary` | Get entity financial summary | Yes | Member |

**Example: Create Entity**
```bash
curl -X POST http://localhost:8002/api/entities \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Smith Family",
    "entity_type": "Home",
    "description": "Family finances"
  }'
```

**Example: Invite Member**
```bash
curl -X POST http://localhost:8002/api/entities/{entity_id}/invite \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "user_email": "member@example.com",
    "role": "member"
  }'
```

**Example: Get Entity Summary (Admin View)**
```bash
curl -X GET "http://localhost:8002/api/entities/{entity_id}/summary?include_private=true" \
  -b cookies.txt
```

## 📜 Script Reference

### Available Scripts

iTrack+ includes 12 essential scripts (6 for Docker, 6 for Local):

#### Docker Scripts
| Script | OS | Purpose |
|--------|----|---------|
| `verify.ps1` / `verify.sh` | Windows / Linux+Mac | Verify Docker installation |
| `start.ps1` / `start.sh` | Windows / Linux+Mac | Start with Docker Compose |
| `stop.ps1` / `stop.sh` | Windows / Linux+Mac | Stop Docker containers |

#### Local Scripts
| Script | OS | Purpose |
|--------|----|---------|
| `setup-local.ps1` / `setup-local.sh` | Windows / Linux+Mac | One-time environment setup |
| `start-local.ps1` / `start-local.sh` | Windows / Linux+Mac | Start backend + frontend (generates on first run `scripts/start-backend.*` and `scripts/start-frontend.*`; will not overwrite existing helpers) |
| `stop-local.ps1` / `stop-local.sh` | Windows / Linux+Mac | Stop all processes |
| `start-backend.ps1` / `start-backend.sh` | Windows / Linux+Mac | Start backend only (from `scripts/`) |
| `start-frontend.ps1` / `start-frontend.sh` | Windows / Linux+Mac | Start frontend only (from `scripts/`) |

### Script Details

#### setup-local (One-time Setup)
**What it does:**
1. ✅ Verifies Python 3.11+ is installed
2. ✅ Verifies Node.js 16+ is installed
3. ✅ Checks MongoDB availability
4. ✅ Creates Python virtual environment
5. ✅ Installs backend dependencies (FastAPI, Motor, PyJWT, etc.)
6. ✅ Installs frontend dependencies (React, Vite, Tailwind, etc.)
7. ✅ Creates `.env` configuration files
8. ✅ Configures MongoDB connection

**When to run:** First time only, or after deleting virtual environment

#### start-local (Daily Use)
**What it does:**
1. ✅ Checks MongoDB service status
2. ✅ Starts backend server (FastAPI on port 8000)
3. ✅ Starts frontend server (Vite on port 3000)
4. ✅ Opens separate terminal windows for each
5. ✅ Creates temporary startup scripts

**Features:**
- Verifies MongoDB is running before starting
- Uses service detection (not mongosh command)
- Proper path resolution for reliability
- User prompt if MongoDB not running
 
**Implementation note:** `start-local` generates centralized helper scripts under the `scripts/` folder (`scripts/start-backend.*` and `scripts/start-frontend.*`) on first run. The generator will skip overwriting those helper scripts if they already exist to preserve local edits. Use the helpers directly to start only the backend or only the frontend during development.

#### stop-local (Shutdown)
**What it does:**
1. ✅ Stops backend process on port 8000
2. ✅ Stops frontend process on port 3000
3. ✅ Checks for remaining Node.js processes
4. ✅ Checks for remaining Python processes
5. ✅ Only terminates itrack-related processes

**Features:**
- Port-based process termination
- Path filtering (only kills itrack processes)
- Leaves MongoDB running
- Safe cleanup

### Recent Script Improvements (January 2025)

#### ✅ Issues Fixed
1. **Encoding Issues**: Removed emoji characters causing PowerShell errors
2. **MongoDB Detection**: Changed from `mongosh` (unreliable) to Windows Service check
3. **Path Handling**: Added proper path resolution with `$scriptDir`
4. **Pydantic v2**: Fixed PyObjectId compatibility in backend models

#### 🗑️ Scripts Removed (Consolidated)
- `start-local-fixed.ps1` - Merged into start-local.ps1
- `stop-all.ps1` - Duplicate of stop-local.ps1
- `check-mongo.ps1` - Integrated into start-local.ps1
- `test-backend.ps1` - Temporary diagnostic script
- Auto-generated temporary files
 - Per-folder startup scripts (`backend/start-backend.ps1`, `frontend/start-frontend.ps1`) — consolidated into `scripts/start-backend.*` and `scripts/start-frontend.*`

#### 📊 Cleanup Results
- **Before:** 20 scripts (many redundant)
- **After:** 12 scripts (all necessary)
- **Reduction:** 40% fewer files
- **Status:** 100% functional

---

## 🔧 Troubleshooting

### Docker Issues

#### Docker Daemon Not Running
```bash
# Windows: Start Docker Desktop from Start Menu
# Linux: Start Docker service
sudo systemctl start docker

# macOS: Start Docker Desktop from Applications
```

#### Port Already in Use
```bash
# Check what's using the port
# Windows:
Get-NetTCPConnection -LocalPort 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Linux/macOS:
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

#### Container Build Failures
```bash
# Clear Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

### Local Setup Issues

#### MongoDB Connection Error

**Check if MongoDB is running:**
```bash
# Test connection
mongosh --eval "db.runCommand({ ping: 1 })"

# If not running, start it:
# Windows (service):
net start MongoDB

# Linux:
sudo systemctl start mongod
sudo systemctl status mongod

# macOS:
brew services start mongodb-community
brew services list
```

**Common MongoDB Issues:**
1. Port 27017 already in use
2. Data directory doesn't exist (`/data/db` or `C:\data\db`)
3. Permission issues on data directory
4. Firewall blocking port 27017

**Create data directory:**
```bash
# Linux/macOS:
sudo mkdir -p /data/db
sudo chown -R $USER:$USER /data/db

# Windows (PowerShell as Administrator):
New-Item -Path C:\data\db -ItemType Directory -Force
```

#### Python Module Not Found
```bash
cd backend

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Node Dependencies Not Installed
```bash
cd frontend

# Clear and reinstall
rm -rf node_modules package-lock.json  # Linux/macOS
Remove-Item -Recurse -Force node_modules, package-lock.json  # Windows

npm install
```

#### Backend Won't Start (Port 8000)
```bash
# Kill process on port 8000
# Windows:
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Linux/macOS:
lsof -ti:8000 | xargs kill -9

# Then restart backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Won't Start (Port 3000)
```bash
# Kill process on port 3000
# Windows:
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force

# Linux/macOS:
lsof -ti:3000 | xargs kill -9

# Then restart frontend
cd frontend
npm run dev
```

#### Cannot Connect to Backend API

1. **Verify backend is running:**
  ```bash
  curl http://localhost:8002/docs
  # Should return Swagger UI HTML
  ```

2. **Check `frontend/.env` file:**
  ```bash
  # Should contain:
  VITE_API_URL=http://localhost:8002
  ```

3. **Clear browser cache:**
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Option+E

4. **Check browser console for CORS errors:**
   - Open DevTools (F12)
   - Look for CORS-related errors
   - Verify `FRONTEND_URL` in backend `.env`

### Database Issues

#### MongoDB Won't Start

**Windows:**
```powershell
# Check service status
Get-Service MongoDB

# Check data directory exists
Test-Path C:\data\db

# View logs
Get-Content "C:\Program Files\MongoDB\Server\7.0\log\mongod.log" -Tail 50

# Restart service
Restart-Service MongoDB
```

**Linux:**
```bash
# Check status
sudo systemctl status mongod

# View logs
sudo journalctl -u mongod -n 50

# Check data directory
ls -la /var/lib/mongodb

# Check configuration
cat /etc/mongod.conf

# Restart service
sudo systemctl restart mongod
```

**macOS:**
```bash
# Check if running
brew services list

# View logs
tail -f /usr/local/var/log/mongodb/mongo.log

# Restart service
brew services restart mongodb-community
```

#### Can't Connect to MongoDB

```bash
# Test local connection
mongosh mongodb://localhost:27017

# If using Atlas, test connection string
mongosh "mongodb+srv://username:password@cluster.mongodb.net/test"

# Check if port is open
netstat -an | grep 27017  # Linux/macOS
Get-NetTCPConnection -LocalPort 27017  # Windows
```

#### Database Backup and Restore

**Backup:**
```bash
# Backup entire database
mongodump --db itrack_db --out ./backup-$(date +%Y%m%d)

# Backup specific collection
mongodump --db itrack_db --collection transactions --out ./backup
```

**Restore:**
```bash
# Restore database
mongorestore --db itrack_db ./backup-20240101/itrack_db

# Drop existing and restore
mongorestore --db itrack_db --drop ./backup-20240101/itrack_db
```

### Common Error Messages

#### "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Activate virtual environment and install dependencies
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### "Error: Cannot find module 'react'"
**Solution:** Install frontend dependencies
```bash
cd frontend
npm install
```

#### "pymongo.errors.ServerSelectionTimeoutError"
**Solution:** MongoDB is not running or not accessible
```bash
# Check if MongoDB is running
mongosh --eval "db.runCommand({ ping: 1 })"

# Check MONGODB_URL in .env file
cat .env | grep MONGODB_URL
```

#### "CORS policy: No 'Access-Control-Allow-Origin' header"
**Solution:** Update `FRONTEND_URL` in backend `.env`
```bash
# In backend .env file:
FRONTEND_URL=http://localhost:3000

# Restart backend after changing
```

### Performance Issues

#### Slow Docker Performance (Windows)
**Solution:** Ensure WSL 2 is properly configured
```powershell
# Check WSL version
wsl -l -v

# Should show VERSION 2
# If not, upgrade:
wsl --set-version Ubuntu 2
```

#### High Memory Usage
**Solution:** Limit Docker resources
```yaml
# In docker-compose.yml, add to services:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Development Tools

### Developer Notes (Recent Functional Changes)

These notes document recent functional changes that developers should be aware of and how to adapt local environments or perform migrations.

- Recurring transactions: Transactions now support recurring flags and metadata on the model: `is_recurring` (bool), `recurrence` (currently `'monthly'`), and `recurrence_start` (ISO datetime). When rendering or summarizing monthly views, recurring monthly items are included when active for the month.

- Bulk import: Frontend includes an Excel-style bulk input component that can POST a JSON array to the backend bulk-create endpoint at `POST /api/transactions/bulk`. The backend validates each item using the existing `TransactionCreate` schema and performs an `insert_many` for atomic-ish bulk inserts.

- API: The summary endpoint `GET /api/transactions/summary` accepts optional query parameters `year` and `month` to return a month-specific summary that includes active recurring monthly items.

- Pagination caps: Transaction listing defaults to `limit=50` and enforces a maximum of `200` to avoid high memory usage on the server.

- Redis (optional but recommended in production):
  - When `REDIS_URL` is set, the app uses Redis for JWT blocklist persistence and for distributed rate-limiting (slowapi storage). This is recommended for multi-instance deployments.

- Sentry: Set `SENTRY_DSN` in environment to enable Sentry error reporting.

- Migration notes:
  - Existing transaction documents should be backfilled with default fields: `is_recurring: false`, `recurrence: null`, `recurrence_start: null`.
  - Recommended index additions to support monthly queries efficiently: index on `date`, and compound indexes on `is_recurring` + `recurrence` + `recurrence_start` as needed for aggregation performance.

Add migration scripts or a one-off script to populate the new fields for existing documents before enabling monthly summaries in production.

#### View Database Contents

**Using MongoDB Shell:**
```bash
mongosh
use itrack_db
show collections
db.users.find().pretty()
db.transactions.find().limit(10).pretty()
db.entities.find().pretty()
```

**Using MongoDB Compass (GUI):**
1. Download from [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect to `mongodb://localhost:27017`
3. Browse `itrack_db` database
4. View collections visually

#### Debug Backend Issues

```bash
# Run with debug logging
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug

# Check backend logs
tail -f backend.log
```

#### Debug Frontend Issues

```bash
# Run with verbose logging
cd frontend
npm run dev -- --debug

# Check browser console (F12)
# Check Network tab for API calls
```

### Getting Help

1. **Check logs:**
   - Backend: Terminal output or `backend.log`
   - Frontend: Terminal output or browser console
   - MongoDB: `/var/log/mongodb/mongod.log`

2. **Verify configuration:**
   ```bash
   # Check .env file
   cat .env

   # Check frontend .env
   cat frontend/.env
   ```

3. **Test API directly:**
   ```bash
  # Test backend health
  curl http://localhost:8002/docs

   # Test MongoDB connection
   mongosh --eval "db.runCommand({ ping: 1 })"
   ```

4. **Check running processes:**
   ```bash
   # Check ports in use
   # Windows:
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000

   # Linux/macOS:
   lsof -i :8000
   lsof -i :3000
   ```

---

## 🔧 Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `MONGODB_URL` - MongoDB connection string
- `SECRET_KEY` - JWT secret key (generate with `openssl rand -hex 32`)
- `FRONTEND_URL` - CORS origin
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `ENVIRONMENT` - development | production

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up --build

# Start in detached mode
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using FastAPI, React, TypeScript, and MongoDB
