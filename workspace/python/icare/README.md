# iCare+ — Clinic Management System

A full-stack medical clinic management system for managing doctors, patients, appointments, scheduling, billing, and invoicing. Built with Flask (REST API + SSR frontend) and PostgreSQL.

**Core Technologies**: Flask REST API · Flask Jinja2 Frontend · PostgreSQL 14+ · Token-based Authentication · Role-based Access Control

## Architecture

| Component | Technology | Default Port |
|-----------|-----------|:---:|
| REST API | Flask + psycopg2 + itsdangerous | 8004 |
| Web App | Flask SSR + Jinja2 + Chart.js | 3003 |
| Database | PostgreSQL 14+ | 5432 |

## Key Features

### ✅ Core Clinical Features
- **Specialities** — Create and manage medical specialties
- **Doctors** — Add doctors with assigned specialties and schedules
- **Patients** — Manage patient records with contact details
- **Schedules** — Configure doctor working hours by day/time
- **Appointments** — Book appointments with availability validation and overlap prevention
- **Leaves** — Track doctor leaves and holidays
- **Case History** — Maintain patient visit records

### ✅ Authentication & Authorization
- **Token-Based Auth** — Signed, time-limited tokens (24-hour expiry)
- **Role-Based Access Control** — Admin, Doctor, Nurse, Office, Billing, Security roles
- **User Management** — Admin can create/edit/delete users with role assignment
- **Role Management** — Admin can create, edit, and delete custom roles
- **Permission Management** — Admin-friendly UI to configure screen access and action permissions per role
  - Quick Permission Editing — Manage permissions directly from role edit modal (3-tab interface)
  - Admin Permissions Panel — Comprehensive permission matrix at `/admin/permissions`
  - Permission-Based UI — Action buttons (New/Edit/Delete) hidden based on user permissions
- **Default Admin** — Built-in admin user (username: `admin`, password: `admin`)

### ✅ Billing & Invoicing
- **Invoices** — Create invoices with line items (description, qty, unit price)
- **Auto-numbering** — Invoices numbered as `INV-YYYYMM-{id}`
- **Payments** — Record payment transactions with amount, date, method, reference
- **Outstanding Tracking** — Automatic calculation of paid vs outstanding amounts
- **Invoice Export** — PDF export with reportlab
- **Multi-format Reports** — CSV, Excel, PDF exports for monthly/yearly billing data

### ✅ Financial Reporting
- **Transactions** — Track income and expense transactions by category
- **Billing Dashboard** — Visual charts (Chart.js) showing monthly income/expenses/profit
- **Monthly Breakdown** — Detailed tables with monthly financial summaries
- **Period/Year Filtering** — Filter reports by month or full year

### ✅ User Interface
- **Login Screen** — Secure login with hidden menu until authentication
- **Responsive Design** — Tailwind CSS + theme switcher (12 themes)
- **Dashboard** — Welcome screen with doctor/speciality browser
- **Navigation** — Context-aware menu (shows only authenticated user's available options)

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 14+
- PowerShell (Windows) or Bash (macOS/Linux)

### 1. Configure Environment

```bash
# Copy example config
# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
copy .env.example .env

# Edit .env and set at minimum:
# DB_PASSWORD=your_postgres_password
```

### 2. Create Database

```bash
# Linux / macOS
psql -U postgres -f clinic_setup.sql

# Windows (PowerShell)
$env:PGPASSWORD='postgres'; psql -U postgres -f clinic_setup.sql
```

### 3. Setup (Install Dependencies)

```bash
# Linux / macOS
./scripts/setup.sh

# Windows (PowerShell)
.\scripts\setup.ps1
```

### 4. Start Services

```bash
# Linux / macOS
./scripts/start.sh

# Windows (PowerShell)
.\scripts\start.ps1
```

**Output:**
```
iCare+ is running!

  Web app  ->  http://localhost:3003
  API      ->  http://localhost:8004

To stop: .\scripts\stop.ps1
```

### 5. Login
- Open http://localhost:3003
- Login with **admin / admin**
- Navigate to Users to create additional accounts with roles

## API Reference

### Base URL
`http://localhost:${API_PORT:-8004}`

### Authentication
All endpoints (except `/auth/login`) require:
```
Authorization: Bearer <token>
```
Tokens expire after 24 hours (configurable via `API_TOKEN_EXP` env var).

### Core Endpoints

#### Authentication
- **POST /auth/login** — Login with username/password
  ```json
  Request:  { "username": "admin", "password": "admin" }
  Response: { "user": {...}, "token": "eyJ..." }
  ```

#### Users (Admin only)
- **GET /users** — List all users (requires Admin role)
- **POST /users** — Create user (requires Admin role)
  ```json
  { "username": "john", "password": "pass", "full_name": "John Doe", 
    "email": "john@clinic.com", "role": "Doctor", "is_admin": false }
  ```
- **PUT /users/<id>** — Update user (requires Admin role)
- **DELETE /users/<id>** — Delete user (requires Admin role)

#### Roles (Admin only)
- **GET /roles** — List all roles (public)
- **POST /roles** — Create role (requires Admin role)
- **PUT /roles/<name>** — Update role name/description (requires Admin role)
- **DELETE /roles/<name>** — Delete role (requires Admin role)

#### Specialities
- **GET /specialities** — List specialties
- **POST /specialities** — Create (JSON: `{ "name": "...", "description": "..." }`)
- **PUT /specialities/<id>** — Update
- **DELETE /specialities/<id>** — Delete

#### Doctors
- **GET /doctors** — List doctors
- **GET /doctors/<id>** — Doctor details (includes schedules)
- **POST /doctors** — Create
- **PUT /doctors/<id>** — Update
- **DELETE /doctors/<id>** — Delete (blocked if pending appointments)
- **GET /doctors/<id>/schedules** — List schedules
- **POST /doctors/<id>/schedules** — Add schedule
- **GET /doctors/<id>/available_slots?date=YYYY-MM-DD&slot=10** — Check availability

#### Patients
- **GET /patients** — List patients
- **GET /patients/<id>** — Patient details
- **POST /patients** — Create
- **PUT /patients/<id>** — Update
- **DELETE /patients/<id>** — Delete (blocked if pending appointments)

#### Appointments
- **GET /appointments** — List appointments (query params: doctor_id, patient_id, date)
- **POST /appointments** — Book appointment
  ```json
  { "doctor_id": 1, "patient_id": 1, "date": "2026-08-20", "time": "09:00", "duration": 10 }
  ```
- **DELETE /appointments/<id>** — Cancel appointment

#### Invoices (Billing role or Admin)
- **GET /invoices** — List invoices
- **POST /invoices** — Create invoice with line items
  ```json
  { "invoice_date": "2026-08-14", "patient_id": 1,
    "lines": [{ "description": "Consultation", "qty": 1, "unit_price": 100.00 }] }
  ```
- **GET /invoices/<id>** — Invoice details (includes lines, payments, outstanding)
- **PUT /invoices/<id>** — Update invoice
- **DELETE /invoices/<id>** — Delete invoice
- **GET /invoices/<id>/export** — Export as PDF
- **POST /invoices/<id>/lines** — Add line item

#### Payments (Billing role or Admin)
- **GET /payments** — List all payments
- **POST /payments** — Record payment
  ```json
  { "invoice_id": 1, "amount": 50.00, "payment_date": "2026-08-14",
    "method": "cash", "reference": "PV-001" }
  ```
- **DELETE /payments/<id>** — Delete payment

#### Transactions (Billing role or Admin)
- **GET /billing/transactions** — List transactions (query param: type=income|expense)
- **POST /billing/transactions** — Create transaction
  ```json
  { "trans_date": "2026-08-14", "amount": 1000.00, "type": "income",
    "category_id": null, "description": "Consultation fees" }
  ```
- **PUT /billing/transactions/<id>** — Update transaction
- **DELETE /billing/transactions/<id>** — Delete transaction

#### Reports
- **GET /reports/billing** — Financial summary (query params: period=YYYY-MM or year=YYYY; format=json|csv|xls|pdf)
  ```
  Response: { "income": 5000.00, "expenses": 1500.00, "profit": 3500.00, "by_month": [...] }
  ```

### Example API Calls

```bash
# Login
curl -X POST http://localhost:8004/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Extract token from response, then use it:
TOKEN="eyJ..."

# List doctors
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8004/doctors

# Create patient
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john@example.com","phone":"555-1234"}' \
  http://localhost:8004/patients

# Book appointment
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"doctor_id":1,"patient_id":1,"date":"2026-08-20","time":"10:00","duration":10}' \
  http://localhost:8004/appointments

# Create invoice
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invoice_date":"2026-08-14","patient_id":1,"lines":[{"description":"Consultation","qty":1,"unit_price":100}]}' \
  http://localhost:8004/invoices
```

## Configuration

All settings are loaded from `.env` at startup:

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | localhost | PostgreSQL host |
| DB_PORT | 5432 | PostgreSQL port |
| DB_NAME | clinic | Database name |
| DB_USER | postgres | DB username |
| DB_PASSWORD | postgres | DB password |
| API_PORT | 8004 | REST API port |
| WEB_PORT | 3003 | Frontend server port |
| API_URL | http://localhost:8004 | API URL (used by web app) |
| API_SECRET | dev-secret | Secret for signing tokens |
| API_TOKEN_EXP | 86400 | Token expiry in seconds (24 hours) |
| WEB_SECRET | dev-secret | Secret for Flask session |

## Roles & Permissions

### Overview
iCare features a comprehensive **role-based access control (RBAC)** system with:
- **Database-level permission enforcement** (read-only vs read-write)
- **Admin UI for managing permissions** via web interface
- **Automatic permission checks** on all data-modifying endpoints
- **Screen-level access control** with automatic menu filtering

### Permission Model

The system uses two database tables for granular control:

```sql
screen_role_permissions (role_name, screen_name)
  └─ Maps which screens each role can access

action_permissions (role_name, screen_name, action)
  └─ Maps which actions (view/add/edit/delete) each role can perform on each screen
```

### Available Screens
- `appointments` - Appointment booking and management
- `patients` - Patient records
- `doctors` - Doctor management
- `specialities` - Medical specialties
- `invoices` - Invoice management
- `transactions` - Payment and financial transactions
- `dashboard` - Analytics and reporting dashboard
- `users` - User management (admin only)
- `roles` - Role management (admin only)

### Available Actions
- **view** - Read/display data on a screen
- **add** - Create new records
- **edit** - Modify existing records
- **delete** - Remove records

### Default Role Configuration

| Role | Screens | Actions | Purpose |
|------|---------|---------|---------|
| **Admin** | All screens | All actions | Full system access; default admin user: `admin/admin` |
| **Doctor** | appointments | view, add, edit | View appointments, add/edit prescriptions |
| **Nurse** | appointments, patients, doctors | view only | Read-only clinical data access |
| **Office** | appointments, patients | view, add, edit | Manage appointments and patient records |
| **Billing** | invoices, transactions, dashboard | view, add, edit | Invoice and payment management |
| **Security** | (none) | (none) | Reserved for future use |

**Note**: All roles are customizable. Admin can create custom roles via the Roles UI or manage permissions directly at `/admin/permissions`

### Admin Has Full Access by Default
- Admin users (with `is_admin=true`) automatically see **ALL screens** in the menu
- Admin users can perform **ANY action** (view/add/edit/delete) on **ANY screen**
- This is enforced at both API and UI levels
- Admin access is determined by the `is_admin` boolean flag in the users table

### How Authorization Works

#### 1. User Login
```
POST /auth/login {username, password}
  └─ Returns token containing {id, is_admin, iat}
```

#### 2. Frontend Menu Filtering
```javascript
// On page load, JavaScript calls:
GET /user/accessible-screens (Bearer token)
  └─ Admin: Returns ALL screens
  └─ Non-Admin: Returns only screens in screen_role_permissions for their role
  └─ Frontend hides menu items not in response
```

#### 3. API Action Enforcement
```python
# When user tries to modify data
POST /invoices {data}
  1. Verify token is valid
  2. Check role membership if required
  3. Check action permission: can_perform_action(user, 'invoices', 'add')
  4. Proceed if authorized, else return 403 Forbidden
```

### API Endpoints for Permission Management

#### Get Current Permissions
```bash
# Requires Admin access
GET /admin/screen-permissions
GET /admin/action-permissions
```

#### Update Permissions
```bash
# Update screen access (which screens each role can see)
PUT /admin/screen-permissions
Content-Type: application/json

{
  "mappings": [
    {"role_name": "Billing", "screen_name": "invoices"},
    {"role_name": "Billing", "screen_name": "transactions"},
    {"role_name": "Billing", "screen_name": "dashboard"}
  ]
}

# Update action permissions (which actions each role can perform)
PUT /admin/action-permissions
Content-Type: application/json

{
  "permissions": [
    {"role_name": "Billing", "screen_name": "invoices", "action": "view"},
    {"role_name": "Billing", "screen_name": "invoices", "action": "add"},
    {"role_name": "Billing", "screen_name": "invoices", "action": "edit"}
  ]
}
```

#### Get User's Accessible Screens
```bash
GET /user/accessible-screens
Authorization: Bearer {token}

# Returns list of screens user can access
# Admin: ["appointments", "patients", "doctors", "specialities", "invoices", "transactions", "dashboard", "users", "roles"]
# Billing: ["dashboard", "invoices", "transactions"]
# Doctor: ["appointments"]
```

### Admin Permissions UI

**URL**: `http://localhost:3003/admin/permissions` (Admin only)

**Features**:
- **Screen Access Tab** - Manage which screens each role can access
  - Matrix of roles × screens with checkboxes
  - Check to grant access, uncheck to revoke
  - Click "Save Screen Permissions"

- **Action Permissions Tab** - Manage which actions each role can perform on each screen
  - Matrix of roles × screens × actions (view/add/edit/delete)
  - Check to grant action, uncheck to revoke
  - Click "Save Action Permissions"

### Role-Based Permission Management (Quick Edit)

When editing a role via the Roles screen (`http://localhost:3003/roles`), you can now manage all permissions directly in a single modal dialog:

**Features**:
- **3-Tab Interface** in the Edit Role modal:
  1. **Role Info Tab** - Edit role name and description
  2. **Screen Access Tab** - Checkbox for each screen (appointments, invoices, patients, etc.)
  3. **Action Permissions Tab** - View/Add/Edit/Delete checkboxes per screen
- **One-Click Save** - Click "Save All Changes" to update role info AND permissions together
- **Real-time Permission Sync** - Permissions reflect current database state when you open the modal
- **Admin Only** - Only admin users can access this feature

### Protected Endpoints

All data-modifying endpoints check action permissions:

#### Appointments
- `POST /appointments` - requires 'add' permission
- `DELETE /appointments/<id>` - requires 'delete' permission

#### Invoices
- `POST /invoices` - requires 'add' permission
- `PUT /invoices/<id>` - requires 'edit' permission
- `DELETE /invoices/<id>` - requires 'delete' permission
- `POST /invoices/<id>/lines` - requires 'add' permission

#### Payments/Transactions
- `POST /payments` - requires 'add' permission (transactions screen)
- `DELETE /payments/<id>` - requires 'delete' permission (transactions screen)

#### Patients
- `POST /patients` - requires 'add' permission
- `PUT /patients/<id>` - requires 'edit' permission
- `DELETE /patients/<id>` - requires 'delete' permission

#### Doctors
- `POST /doctors` - requires 'add' permission
- `PUT /doctors/<id>` - requires 'edit' permission
- `DELETE /doctors/<id>` - requires 'delete' permission

#### Specialities
- `POST /specialities` - requires 'add' permission
- `PUT /specialities/<id>` - requires 'edit' permission
- `DELETE /specialities/<id>` - requires 'delete' permission

### Example Permission Scenarios

**Scenario 1: Billing User Creates Invoice**
```
1. Frontend calls POST /invoices
2. API verifies token and gets user.role = 'Billing'
3. Checks: can_perform_action(user, 'invoices', 'add')
4. Queries action_permissions table for Billing + invoices + add
5. Permission found ✅ → Invoice created (201 Created)
```

**Scenario 2: Doctor Tries to Delete Invoice**
```
1. Frontend calls DELETE /invoices/123
2. API verifies token and gets user.role = 'Doctor'
3. Checks: can_perform_action(user, 'invoices', 'delete')
4. Queries action_permissions table for Doctor + invoices + delete
5. No permission found ❌ → Returns 403 Forbidden
   "You do not have permission to delete invoices"
```

**Scenario 3: Admin Updates Doctor's Screen Access**
```
1. Admin goes to http://localhost:3003/admin/permissions
2. Unchecks "Doctor → [dashboard, doctors, patients]"
3. Leaves checked only "Doctor → [appointments]"
4. Clicks "Save Screen Permissions"
5. API updates screen_role_permissions table
6. Next time Doctor logs in, menu only shows Appointments
7. API returns 403 Forbidden for any other screens
```

### Managing Permissions

**Via Role Edit Modal (Fastest)**:
1. Login as admin user
2. Navigate to http://localhost:3003/roles
3. Click "Edit" on any role
4. Switch between the 3 tabs to manage all aspects of the role:
   - **Role Info**: Change name and description
   - **Screen Access**: Check/uncheck which screens the role can access
   - **Action Permissions**: Check/uncheck what actions (view/add/edit/delete) the role can perform per screen
5. Click "Save All Changes" to save everything at once

**Via Admin Permissions Panel (Comprehensive)**:
1. Login as admin user
2. Navigate to http://localhost:3003/admin/permissions
3. Adjust permissions using checkboxes
4. Click Save for each section

**Programmatically via API**:
```bash
# Get current permissions
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8004/admin/screen-permissions

# Update permissions
curl -X PUT -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mappings":[{"role_name":"Doctor","screen_name":"invoices"}]}' \
  http://localhost:8004/admin/screen-permissions
```

**Directly in Database** (Emergency only):
```sql
-- Check permissions for a role
SELECT screen_name FROM screen_role_permissions 
WHERE role_name = 'Billing' ORDER BY screen_name;

SELECT screen_name, action FROM action_permissions 
WHERE role_name = 'Billing' ORDER BY screen_name, action;

-- Revoke permission
DELETE FROM action_permissions 
WHERE role_name = 'Doctor' AND action = 'delete';
```

### Permission-Based UI Visibility

The frontend automatically hides action buttons based on user permissions for a better user experience:

**Action Buttons That Respect Permissions**:
- **"New" Buttons** (Add) - Hidden if user lacks 'add' permission
  - "New Invoice", "New Transaction", "New Patient", "New Doctor", "New User", etc.
- **Edit Links/Buttons** - Hidden if user lacks 'edit' permission
  - Edit links in data tables
- **Delete Buttons** - Hidden if user lacks 'delete' permission
  - Delete buttons in action columns

**Example: Billing User with View-Only Transactions**
```
Permissions: transactions → view only (no add/edit/delete)
Result when viewing /billing/transactions:
  ✓ Can see transaction list
  ✗ "New Transaction" button hidden
  ✗ Edit links hidden
  ✗ Delete buttons hidden
  ✓ Can view transaction details
```

**Example: Billing User with Full Invoice Access**
```
Permissions: invoices → view, add, edit (no delete)
Result when viewing /invoices:
  ✓ "New Invoice" button visible
  ✓ Edit links visible
  ✗ Delete buttons hidden
  ✓ Can create and edit invoices but not delete
```

**How It Works**:
1. Frontend JavaScript calls `/admin/action-permissions` API
2. Checks if user has permission for each action
3. Admin users automatically see all buttons (is_admin=true bypass)
4. Non-admin users see only buttons for actions they're allowed to perform
5. If API fails, buttons are shown (fail-open for better UX)

**Note**: Frontend hiding is a UX enhancement. The backend API enforces the actual security - users cannot bypass permissions by manually editing HTML.


```bash
# Test 1: Admin can access all screens
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8004/user/accessible-screens
# Expected: ["appointments", "patients", "doctors", "specialities", 
#            "invoices", "transactions", "dashboard", "users", "roles"]

# Test 2: Billing user can only access billing screens
curl -H "Authorization: Bearer $BILLING_TOKEN" \
  http://localhost:8004/user/accessible-screens
# Expected: ["dashboard", "invoices", "transactions"]

# Test 3: Permission enforcement
curl -X POST -H "Authorization: Bearer $DOCTOR_TOKEN" \
  http://localhost:8004/invoices
# Expected: 403 Forbidden (Doctor doesn't have 'add' permission for invoices)

# Test 4: Action permission grants
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8004/invoices
# Expected: 201 Created (Admin can perform any action)
```

**UI Visibility Test** (Manual):
1. Login as **admin** → Visit /billing/transactions → See "New Transaction" button ✓
2. Logout and login as **billing user (manoj/manoj)** → Visit /billing/transactions → "New Transaction" button HIDDEN ✓
   - Buttons only appear for actions the billing user is permitted to perform
3. Visit /invoices as billing user → See "New Invoice" button ✓ (has add permission)
   - But "New Transaction" hidden ✓ (has view-only permission)

## Troubleshooting

### Port already in use
```bash
# Windows: Find and kill process using port 8004
netstat -ano | findstr :8004
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8004 | grep LISTEN
kill -9 <PID>
```

### Database connection failed
- Verify PostgreSQL is running: `psql --version`
- Check .env has correct DB credentials
- Run: `psql -U postgres clinic -c "SELECT 1"` to test connection

### Tokens expire too quickly
- Increase `API_TOKEN_EXP` in .env (value is in seconds)
- Restart services after changing

### Dependencies missing
- Run `./scripts/setup.sh` (macOS/Linux) or `.\scripts\setup.ps1` (Windows)
- Or manually: `pip install -r api/requirements.txt && pip install -r web-app/requirements.txt`

## Development Notes

### Project Structure
```
icare/
├── api/
│   ├── app.py              # REST API (Flask)
│   ├── requirements.txt
│   └── venv/
├── web-app/
│   ├── client.py           # Frontend server (Flask SSR)
│   ├── *.html              # Jinja2 templates
│   ├── static/
│   │   └── hospital.jpg
│   ├── requirements.txt
│   └── venv/
├── clinic_setup.sql        # Database initialization
└── scripts/
    ├── start.ps1 / start.sh
    ├── stop.ps1 / stop.sh
    └── setup.ps1 / setup.sh
```

### Technologies
- **Backend**: Flask 2.2+, psycopg2-binary, itsdangerous, reportlab
- **Frontend**: Flask, Jinja2, Tailwind CSS, Chart.js
- **Database**: PostgreSQL 14+
- **Security**: werkzeug.security (password hashing)

### Key Implementation Details
- Tokens: Signed with `itsdangerous.URLSafeTimedSerializer`
- Password hashing: `werkzeug.security.generate_password_hash/check_password_hash`
- Database: Psycopg2 connection pooling via `psycopg2.connect()`
- Runtime migrations: Tables auto-created on first API startup
- PDF export: reportlab `SimpleDocTemplate` for invoices
- Charts: Chart.js for dashboard visualizations
- **Permissions**: 
  - Core function: `can_perform_action(user, screen_name, action)` checks action_permissions table
  - Endpoint decorator: `@require_token(roles=['Billing','Admin'])` checks role membership
  - Menu filtering: Frontend JavaScript fetches `/user/accessible-screens` and hides unauthorized items
  - Action button visibility: Frontend JavaScript calls `/admin/action-permissions` to hide/show Create/Edit/Delete buttons based on user permissions
  - Database tables: `screen_role_permissions` (screen access), `action_permissions` (action-level control)
  - Admin bypass: Any user with `is_admin=true` bypasses all permission checks
  - API enforcement: All POST/PUT/DELETE endpoints include action permission checks before processing
  - Role editing: Quick permission management via 3-tab modal in role edit form (Screen Access + Action Permissions tabs)

## License

MIT License — See LICENSE file

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API logs: `tail -f api.log`
3. Enable debug mode in `.env`: `FLASK_DEBUG=1`
4. Open an issue on GitHub

---

**Last Updated**: 2026-08-14  
**Version**: 2.1 (With Permission-Based UI Visibility + Quick Role Permission Management)
