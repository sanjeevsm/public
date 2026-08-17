import os
import io
import csv
import json
import time as _time
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import g

# Token signer
_API_SECRET = os.getenv('API_SECRET', 'dev-secret')
_TOKEN_EXP = int(os.getenv('API_TOKEN_EXP', str(60*60*24)))
_signer = URLSafeTimedSerializer(_API_SECRET)

def generate_token_for(user):
    # embed id and is_admin and issued-at
    payload = {'id': int(user.get('id', 0)), 'is_admin': bool(user.get('is_admin', False)), 'iat': int(_time.time())}
    return _signer.dumps(payload)

def verify_token(token, max_age=_TOKEN_EXP):
    try:
        data = _signer.loads(token, max_age=max_age)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    # fetch user from DB if possible
    uid = data.get('id')
    if not uid:
        return None
    if _use_db():
        rows = query('SELECT id, username, full_name, email, is_admin, role, doctor_id, is_active FROM users WHERE id=%s', (uid,))
        if not rows:
            return None
        u = rows[0]
        if not u.get('is_active'):
            return None
        return u
    else:
        # fallback to admin only
        if uid == 0:
            return {'id': 0, 'username': 'admin', 'full_name': 'Admin', 'email': 'admin@example.com', 'is_admin': True, 'role': 'Admin', 'doctor_id': None, 'is_active': True}
        return None

def require_token(superadmin=False, role=None, roles=None):
    """Decorator to require a valid token. Backwards-compatible.

    - `superadmin=True` requires is_admin flag.
    - `role='billing'` requires user's `role` equals the given role.
    - `roles=['billing','office']` requires user's role in the list.
    """
    def decorator(f):
        def wrapped(*args, **kwargs):
            auth = request.headers.get('Authorization') or request.args.get('token')
            if not auth:
                return fail('authorization required', 401)
            if isinstance(auth, str) and auth.lower().startswith('bearer '):
                token = auth.split(None, 1)[1]
            else:
                token = auth
            user = verify_token(token)
            if not user:
                return fail('invalid or expired token', 401)
            # admin short-circuit
            if superadmin and not user.get('is_admin'):
                return fail('admin access required', 403)
            # role/roles checks
            if role:
                if user.get('role') != role:
                    return fail('role required: %s' % role, 403)
            if roles:
                if user.get('role') not in roles:
                    return fail('one of roles required', 403)
            g.current_user = user
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator


def can_perform_action(user, screen_name, action):
    """Check if user can perform an action on a screen"""
    if not user:
        return False
    
    # Admin bypass
    if user.get('is_admin'):
        return True
    
    user_role = user.get('role')
    if not user_role:
        return False
    
    # Check if role has permission for this action on this screen
    if not _use_db():
        return True  # Allow in fallback mode
    
    rows = query(
        'SELECT 1 FROM action_permissions WHERE role_name=%s AND screen_name=%s AND action=%s',
        (user_role, screen_name, action)
    )
    return bool(rows)


def doctor_owns_appointment(doctor_id, appointment_id):
    """Check if doctor owns/created the appointment"""
    if not _use_db():
        return True
    rows = query('SELECT 1 FROM appointments WHERE id=%s AND doctor_id=%s', (appointment_id, doctor_id))
    return bool(rows)

from werkzeug.exceptions import HTTPException
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app)

# Set DB_PASSWORD before starting:
#   Windows (PowerShell): $env:DB_PASSWORD="yourpassword"
#   macOS/Linux:          export DB_PASSWORD="yourpassword"
DB = dict(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', '5432')),
    dbname=os.getenv('DB_NAME', 'clinic'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
)


def get_conn():
    return psycopg2.connect(**DB)


def query(sql, params=None):
    c = get_conn()
    try:
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        c.commit()
        if cur.description:
            result = [_clean(dict(row)) for row in cur.fetchall()]
        else:
            result = {'rows': cur.rowcount}
        cur.close()
        return result
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def _clean(row):
    for k, v in row.items():
        if isinstance(v, (datetime, date)):
            row[k] = v.isoformat()
        elif isinstance(v, time):
            row[k] = v.strftime('%H:%M:%S')
        elif isinstance(v, Decimal):
            row[k] = float(v)
    return row


def ok(data, code=200):
    return jsonify(data), code


def fail(msg, code=400):
    return jsonify({'error': msg}), code


@app.errorhandler(Exception)
def handle_exception(e):
    # Preserve HTTP exceptions (404, 400, etc.) so clients see correct status codes.
    if isinstance(e, HTTPException):
        return fail(e.description or str(e), e.code or 500)
    return fail(str(e), 500)

# Minimal API routes for local development and tests.
# The code prefers the PostgreSQL database but falls back to an
# in-memory sample dataset when a DB connection cannot be established.

# In-memory fallback data and helpers ------------------------------------------------
_FALLBACK = {
    'specialities': [
        {'id': 1, 'name': 'General Practice'},
        {'id': 2, 'name': 'Cardiology'},
        {'id': 3, 'name': 'Dermatology'},
    ],
}

def _use_db():
    try:
        # quick test connection
        conn = get_conn()
        conn.close()
        return True
    except Exception:
        return False


# Ensure users table exists and seed default admin
def ensure_users_table_and_admin():
    if not _use_db():
        return
    # create users table if missing
    sql = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) NOT NULL UNIQUE,
        password_hash VARCHAR(200) NOT NULL,
        full_name VARCHAR(200),
        email VARCHAR(200),
        is_admin BOOLEAN NOT NULL DEFAULT FALSE,
        role VARCHAR(50),
        doctor_id INT REFERENCES doctors(id) ON DELETE SET NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    '''
    query(sql)
    # ensure role column exists (safe for older installs)
    try:
        query("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50)")
    except Exception:
        pass
    # ensure is_admin column exists (safe for older installs)
    try:
        query("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;")
    except Exception:
        pass
    # ensure doctor_id column exists (safe for older installs)
    try:
        query("ALTER TABLE users ADD COLUMN IF NOT EXISTS doctor_id INT REFERENCES doctors(id) ON DELETE SET NULL")
    except Exception:
        pass
    
    # create roles table and seed defaults
    rsql = '''
    CREATE TABLE IF NOT EXISTS user_roles (
        name VARCHAR(50) PRIMARY KEY,
        description TEXT
    );
    '''
    query(rsql)
    # seed common roles if missing
    defaults = [('Admin','Administrator role with full access'),('Doctor','Healthcare provider'),('Nurse','Nursing staff'),('Office','Office management'),('Billing','Billing and finance'),('Security','Security staff')]
    for rn, desc in defaults:
        rows = query('SELECT name FROM user_roles WHERE name=%s', (rn,))
        if not rows:
            query('INSERT INTO user_roles (name, description) VALUES (%s,%s)', (rn, desc))
    # ensure default admin exists (username: admin, password: admin)
    rows = query("SELECT id FROM users WHERE username=%s", ('admin',))
    if not rows:
        pw = generate_password_hash('admin')
        query('INSERT INTO users (username, password_hash, full_name, email, is_admin, role) VALUES (%s,%s,%s,%s,%s,%s)', ('admin', pw, 'Admin', 'admin@example.com', True, 'Admin'))


def ensure_billing_tables():
    if not _use_db():
        return
    # billing_categories (optional)
    query('''
    CREATE TABLE IF NOT EXISTS billing_categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT
    );
    ''')
    # billing transactions
    query('''
    CREATE TABLE IF NOT EXISTS billing_transactions (
        id SERIAL PRIMARY KEY,
        trans_date DATE NOT NULL,
        amount NUMERIC(12,2) NOT NULL,
        type VARCHAR(10) NOT NULL CHECK (type IN ('income','expense')),
        category_id INT REFERENCES billing_categories(id),
        description TEXT,
        created_by INT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    ''')
    # invoices and lines
    query('''
    CREATE TABLE IF NOT EXISTS invoices (
        id SERIAL PRIMARY KEY,
        invoice_no VARCHAR(100) UNIQUE,
        patient_id INT,
        doctor_id INT,
        invoice_date DATE NOT NULL,
        total NUMERIC(12,2) DEFAULT 0,
        status VARCHAR(50) DEFAULT 'draft',
        created_by INT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    ''')
    query('''
    CREATE TABLE IF NOT EXISTS invoice_lines (
        id SERIAL PRIMARY KEY,
        invoice_id INT REFERENCES invoices(id) ON DELETE CASCADE,
        description TEXT,
        qty INT DEFAULT 1,
        unit_price NUMERIC(12,2) DEFAULT 0,
        amount NUMERIC(12,2) DEFAULT 0
    );
    ''')
    query('''
    CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        invoice_id INT REFERENCES invoices(id) ON DELETE CASCADE,
        amount NUMERIC(12,2) NOT NULL,
        payment_date DATE NOT NULL,
        method VARCHAR(100),
        reference VARCHAR(200),
        created_by INT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    ''')


def ensure_permission_tables():
    """Create permission control tables for role-based access control"""
    if not _use_db():
        return
    # Screen-role permissions: which roles can see which screens
    query('''
    CREATE TABLE IF NOT EXISTS screen_role_permissions (
        id SERIAL PRIMARY KEY,
        screen_name VARCHAR(100) NOT NULL,
        role_name VARCHAR(50) NOT NULL,
        UNIQUE(screen_name, role_name)
    );
    ''')
    # Action permissions: which actions (add/edit/delete/view) each role can perform on each screen
    query('''
    CREATE TABLE IF NOT EXISTS action_permissions (
        id SERIAL PRIMARY KEY,
        role_name VARCHAR(50) NOT NULL,
        screen_name VARCHAR(100) NOT NULL,
        action VARCHAR(20) NOT NULL CHECK (action IN ('view','add','edit','delete')),
        UNIQUE(role_name, screen_name, action)
    );
    ''')
    # Seed default permissions if tables are empty
    existing = query('SELECT COUNT(*) as cnt FROM screen_role_permissions')
    if existing and existing[0].get('cnt', 0) == 0:
        # Default screen mappings
        screen_role_defaults = [
            ('appointments', 'Admin'), ('appointments', 'Doctor'), ('appointments', 'Nurse'), ('appointments', 'Office'),
            ('patients', 'Admin'), ('patients', 'Doctor'), ('patients', 'Nurse'), ('patients', 'Office'),
            ('doctors', 'Admin'), ('doctors', 'Doctor'), ('doctors', 'Nurse'),
            ('specialities', 'Admin'),
            ('invoices', 'Admin'), ('invoices', 'Billing'),
            ('transactions', 'Admin'), ('transactions', 'Billing'),
            ('dashboard', 'Admin'), ('dashboard', 'Billing'), ('dashboard', 'Doctor'),
            ('users', 'Admin'),
            ('roles', 'Admin'),
        ]
        for screen, role in screen_role_defaults:
            try:
                query('INSERT INTO screen_role_permissions (screen_name, role_name) VALUES (%s, %s)', (screen, role))
            except Exception:
                pass
    else:
        # Even if table has data, ensure Admin has access to all screens
        all_screens = ['appointments', 'patients', 'doctors', 'specialities', 'invoices', 'transactions', 'dashboard', 'users', 'roles']
        for screen in all_screens:
            try:
                query('INSERT INTO screen_role_permissions (screen_name, role_name) VALUES (%s, %s) ON CONFLICT DO NOTHING', (screen, 'Admin'))
            except Exception:
                # Fallback if ON CONFLICT not supported
                existing = query('SELECT 1 FROM screen_role_permissions WHERE screen_name=%s AND role_name=%s', (screen, 'Admin'))
                if not existing:
                    try:
                        query('INSERT INTO screen_role_permissions (screen_name, role_name) VALUES (%s, %s)', (screen, 'Admin'))
                    except Exception:
                        pass
    # Default action permissions
    existing = query('SELECT COUNT(*) as cnt FROM action_permissions')
    if existing and existing[0].get('cnt', 0) == 0:
        action_defaults = [
            # Admin: full access
            ('Admin', 'appointments', 'view'), ('Admin', 'appointments', 'add'), ('Admin', 'appointments', 'edit'), ('Admin', 'appointments', 'delete'),
            ('Admin', 'patients', 'view'), ('Admin', 'patients', 'add'), ('Admin', 'patients', 'edit'), ('Admin', 'patients', 'delete'),
            ('Admin', 'doctors', 'view'), ('Admin', 'doctors', 'add'), ('Admin', 'doctors', 'edit'), ('Admin', 'doctors', 'delete'),
            ('Admin', 'invoices', 'view'), ('Admin', 'invoices', 'add'), ('Admin', 'invoices', 'edit'), ('Admin', 'invoices', 'delete'),
            ('Admin', 'transactions', 'view'), ('Admin', 'transactions', 'add'), ('Admin', 'transactions', 'edit'), ('Admin', 'transactions', 'delete'),
            ('Admin', 'users', 'view'), ('Admin', 'users', 'add'), ('Admin', 'users', 'edit'), ('Admin', 'users', 'delete'),
            # Doctor: view only + edit own appointments
            ('Doctor', 'appointments', 'view'), ('Doctor', 'patients', 'view'), ('Doctor', 'doctors', 'view'),
            ('Doctor', 'dashboard', 'view'),
            # Billing: view and manage invoices/transactions
            ('Billing', 'invoices', 'view'), ('Billing', 'invoices', 'add'), ('Billing', 'invoices', 'edit'),
            ('Billing', 'transactions', 'view'), ('Billing', 'transactions', 'add'), ('Billing', 'transactions', 'edit'),
            ('Billing', 'dashboard', 'view'),
            # Office: manage appointments and patients (view, add, edit but not delete)
            ('Office', 'appointments', 'view'), ('Office', 'appointments', 'add'), ('Office', 'appointments', 'edit'),
            ('Office', 'patients', 'view'), ('Office', 'patients', 'add'), ('Office', 'patients', 'edit'),
            ('Office', 'doctors', 'view'),
        ]
        for role, screen, action in action_defaults:
            try:
                query('INSERT INTO action_permissions (role_name, screen_name, action) VALUES (%s, %s, %s)', (role, screen, action))
            except Exception:
                pass


def ensure_appointments_columns():
    """Ensure appointments table has prescription column"""
    if not _use_db():
        return
    try:
        query("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS prescription TEXT")
    except Exception:
        pass


try:
    if _use_db():
        ensure_billing_tables()
except Exception:
    pass

# call on import if DB available
try:
    if _use_db():
        ensure_users_table_and_admin()
except Exception:
    # don't crash startup on migration errors
    pass

try:
    if _use_db():
        ensure_permission_tables()
except Exception:
    pass

try:
    if _use_db():
        ensure_appointments_columns()
except Exception:
    pass

# --- Specialities endpoints -----------------------------------------------------
@app.route('/specialities', methods=['GET'])
def list_specialities():
    if _use_db():
        rows = query('SELECT id, name FROM specialities ORDER BY id')
        return ok(rows)
    else:
        return ok(_FALLBACK['specialities'])


# --- Authentication & Users -------------------------------------------------
@app.route('/auth/login', methods=['POST'])
def auth_login():
    body = request.get_json(force=True, silent=True) or {}
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        return fail('username and password are required', 400)
    if not _use_db():
        # fallback: only admin/admin
        if username == 'admin' and password == 'admin':
            user = {'id': 0, 'username': 'admin', 'full_name': 'Admin', 'email': 'admin@example.com', 'is_admin': True}
            token = generate_token_for(user)
            return ok({'user': user, 'token': token})
        return fail('invalid credentials', 401)
    rows = query('SELECT id, username, password_hash, full_name, email, is_admin, is_active FROM users WHERE username=%s', (username,))
    if not rows:
        return fail('invalid credentials', 401)
    user = rows[0]
    if not user.get('is_active'):
        return fail('account disabled', 403)
    if not check_password_hash(user.get('password_hash',''), password):
        return fail('invalid credentials', 401)
    # remove password_hash before returning
    user.pop('password_hash', None)
    token = generate_token_for(user)
    return ok({'user': user, 'token': token})


@app.route('/users', methods=['GET'])
@require_token(superadmin=True)
def list_users():
    if not _use_db():
        return ok([])
    rows = query('SELECT id, username, full_name, email, role, is_admin, is_active, created_at FROM users ORDER BY id')
    return ok(rows)


@app.route('/users/<int:uid>', methods=['GET'])
@require_token(superadmin=True)
def get_user(uid):
    if not _use_db():
        return fail('not available without DB', 400)
    rows = query('SELECT id, username, full_name, email, role, is_admin, is_active, created_at FROM users WHERE id=%s', (uid,))
    if not rows:
        return fail('user not found', 404)
    return ok(rows[0])


@app.route('/users', methods=['POST'])
@require_token(superadmin=True)
def create_user():
    body = request.get_json(force=True, silent=True) or {}
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        return fail('username and password are required', 400)
    full_name = body.get('full_name')
    email = body.get('email')
    role = body.get('role') or body.get('category') or None
    doctor_id = body.get('doctor_id')
    is_admin = bool(body.get('is_admin')) or (role == 'Admin')
    
    # If role is Doctor, doctor_id is mandatory
    if role == 'Doctor' and not doctor_id:
        return fail('doctor_id is required for Doctor role', 400)
    
    pw_hash = generate_password_hash(password)
    if not _use_db():
        return fail('not available without DB', 400)
    # validate role exists if provided
    if role:
        rrole = query('SELECT name FROM user_roles WHERE name=%s', (role,))
        if not rrole:
            return fail('invalid role', 400)
    
    # validate doctor_id exists if provided
    if doctor_id:
        ddoc = query('SELECT id FROM doctors WHERE id=%s', (doctor_id,))
        if not ddoc:
            return fail('invalid doctor_id', 400)
    
    r = query('INSERT INTO users (username, password_hash, full_name, email, is_admin, doctor_id) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, username, full_name, email, is_admin, doctor_id, is_active',
              (username, pw_hash, full_name, email, is_admin, doctor_id if doctor_id else None))
    # if role provided, update it
    if role:
        query('UPDATE users SET role=%s WHERE username=%s', (role, username))
    return ok(r[0], 201)


@app.route('/users/<int:uid>', methods=['PUT'])
@require_token(superadmin=True)
def update_user(uid):
    body = request.get_json(force=True, silent=True) or {}
    if not _use_db():
        return fail('not available without DB', 400)
    fields = []
    params = []
    if 'password' in body and body.get('password'):
        fields.append('password_hash=%s')
        params.append(generate_password_hash(body.get('password')))
    # role handling
    if 'role' in body and body.get('role') is not None:
        # validate
        rrole = query('SELECT name FROM user_roles WHERE name=%s', (body.get('role'),))
        if not rrole:
            return fail('invalid role', 400)
        fields.append('role=%s')
        params.append(body.get('role'))
        
        # If role is Doctor, doctor_id is mandatory
        if body.get('role') == 'Doctor' and not body.get('doctor_id'):
            return fail('doctor_id is required for Doctor role', 400)
    
    # doctor_id handling
    if 'doctor_id' in body:
        doctor_id = body.get('doctor_id')
        if doctor_id:
            # validate doctor exists
            ddoc = query('SELECT id FROM doctors WHERE id=%s', (doctor_id,))
            if not ddoc:
                return fail('invalid doctor_id', 400)
        fields.append('doctor_id=%s')
        params.append(doctor_id)
    
    for k in ('username','full_name','email','is_admin','is_active'):
        if k in body:
            if k in ('is_admin','is_active'):
                fields.append(f"{k}=%s")
                params.append(bool(body.get(k)))
            else:
                fields.append(f"{k}=%s")
                params.append(body.get(k))
    if not fields:
        return fail('no fields to update', 400)
    params.append(uid)
    sql = f"UPDATE users SET {', '.join(fields)} WHERE id=%s RETURNING id, username, full_name, email, is_admin, role, doctor_id, is_active"
    r = query(sql, tuple(params))
    if not r:
        return fail('not found', 404)
    return ok(r[0])


@app.route('/users/<int:uid>', methods=['DELETE'])
@require_token(superadmin=True)
def delete_user(uid):
    if not _use_db():
        return fail('not available without DB', 400)
    r = query('DELETE FROM users WHERE id=%s RETURNING id', (uid,))
    if not r:
        return fail('not found', 404)
    return ok({'deleted': r[0]['id']})


# --- Roles management -------------------------------------------------------
@app.route('/roles', methods=['GET'])
def list_roles():
    if not _use_db():
        return ok([{'name':'Admin','description':'Administrator'},{'name':'Doctor','description':'Healthcare provider'},{'name':'Nurse','description':'Nursing staff'},{'name':'Office','description':'Office management'},{'name':'Billing','description':'Billing and finance'},{'name':'Security','description':'Security staff'}])
    rows = query('SELECT name, description FROM user_roles ORDER BY name')
    return ok(rows)


@app.route('/roles', methods=['POST'])
@require_token(superadmin=True)
def create_role():
    body = request.get_json(force=True, silent=True) or {}
    name = body.get('name')
    desc = body.get('description')
    if not name:
        return fail('name required', 400)
    if _use_db():
        try:
            r = query('INSERT INTO user_roles (name, description) VALUES (%s,%s) RETURNING name, description', (name, desc))
            return ok(r[0], 201)
        except Exception:
            return fail('could not create role (exists?)', 400)
    else:
        return fail('not available without DB', 400)


@app.route('/roles/<string:rname>', methods=['PUT'])
@require_token(superadmin=True)
def update_role(rname):
    body = request.get_json(force=True, silent=True) or {}
    new_name = body.get('name')
    description = body.get('description')
    if not new_name:
        return fail('name required', 400)
    if _use_db():
        try:
            r = query('UPDATE user_roles SET name=%s, description=%s WHERE name=%s RETURNING name, description', (new_name, description, rname))
            if not r:
                return fail('role not found', 404)
            return ok(r[0])
        except Exception as e:
            return fail(f'could not update role: {str(e)}', 400)
    else:
        return fail('not available without DB', 400)


@app.route('/roles/<string:rname>', methods=['DELETE'])
@require_token(superadmin=True)
def delete_role(rname):
    if _use_db():
        r = query('DELETE FROM user_roles WHERE name=%s RETURNING name', (rname,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['name']})
    else:
        return fail('not available without DB', 400)


# --- Permission Management (Admin only) -----------------------------------------
@app.route('/admin/screen-permissions', methods=['GET'])
@require_token(superadmin=True)
def get_screen_permissions():
    """Get all screen-role mappings"""
    if not _use_db():
        return ok([])
    rows = query('SELECT screen_name, role_name FROM screen_role_permissions ORDER BY screen_name, role_name')
    return ok(rows)


@app.route('/admin/screen-permissions', methods=['PUT'])
@require_token(superadmin=True)
def update_screen_permissions():
    """Update screen-role mappings. Expects array of {screen_name, role_name}"""
    if not _use_db():
        return fail('not available without DB', 400)
    body = request.get_json(force=True, silent=True) or {}
    mappings = body.get('mappings', [])  # list of {screen_name, role_name}
    
    # Delete all existing mappings
    query('DELETE FROM screen_role_permissions')
    
    # Insert new mappings
    for m in mappings:
        screen = m.get('screen_name')
        role = m.get('role_name')
        if screen and role:
            try:
                query('INSERT INTO screen_role_permissions (screen_name, role_name) VALUES (%s, %s)', (screen, role))
            except Exception:
                pass
    
    return ok({'updated': len(mappings)})


@app.route('/admin/action-permissions', methods=['GET'])
@require_token(superadmin=True)
def get_action_permissions():
    """Get all action permissions (view/add/edit/delete per role per screen)"""
    if not _use_db():
        return ok([])
    rows = query('SELECT role_name, screen_name, action FROM action_permissions ORDER BY role_name, screen_name, action')
    return ok(rows)


@app.route('/admin/action-permissions', methods=['PUT'])
@require_token(superadmin=True)
def update_action_permissions():
    """Update action permissions. Expects array of {role_name, screen_name, action}"""
    if not _use_db():
        return fail('not available without DB', 400)
    body = request.get_json(force=True, silent=True) or {}
    permissions = body.get('permissions', [])  # list of {role_name, screen_name, action}
    
    # Delete all existing permissions
    query('DELETE FROM action_permissions')
    
    # Insert new permissions
    for p in permissions:
        role = p.get('role_name')
        screen = p.get('screen_name')
        action = p.get('action')
        if role and screen and action:
            try:
                query('INSERT INTO action_permissions (role_name, screen_name, action) VALUES (%s, %s, %s)', (role, screen, action))
            except Exception:
                pass
    
    return ok({'updated': len(permissions)})


@app.route('/user/accessible-screens', methods=['GET'])
@require_token()
def get_accessible_screens():
    """Return list of screens accessible to the current user based on their role"""
    if not _use_db():
        # fallback: admin sees all screens
        return ok(['appointments', 'patients', 'doctors', 'specialities', 'invoices', 'transactions', 'dashboard', 'users', 'roles'])
    
    user = g.current_user if hasattr(g, 'current_user') else {}
    
    # Admin always has access to all screens
    if user.get('is_admin'):
        return ok(['appointments', 'patients', 'doctors', 'specialities', 'invoices', 'transactions', 'dashboard', 'users', 'roles'])
    
    user_role = user.get('role')
    
    if not user_role:
        return ok([])
    
    # Get all screens accessible to this role
    rows = query('SELECT DISTINCT screen_name FROM screen_role_permissions WHERE role_name=%s ORDER BY screen_name', (user_role,))
    screens = []
    for row in rows:
        if isinstance(row, dict):
            screens.append(row['screen_name'])
        else:
            screens.append(row[0])
    
    return ok(screens)


@app.route('/specialities/<int:sid>', methods=['GET'])
def get_speciality(sid):
    if _use_db():
        rows = query('SELECT id, name FROM specialities WHERE id=%s', (sid,))
        if not rows:
            return fail('not found', 404)
        return ok(rows[0])
    else:
        for s in _FALLBACK['specialities']:
            if s['id'] == sid:
                return ok(s)
        return fail('not found', 404)


@app.route('/specialities', methods=['POST'])
@require_token()
def create_speciality():
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'specialities', 'add'):
        return fail('You do not have permission to add specialities', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    name = body.get('name')
    if not name:
        return fail('name is required', 400)
    if _use_db():
        r = query('INSERT INTO specialities (name) VALUES (%s) RETURNING id, name', (name,))
        return ok(r[0], 201)
    else:
        new_id = max([s['id'] for s in _FALLBACK['specialities']] or [0]) + 1
        s = {'id': new_id, 'name': name}
        _FALLBACK['specialities'].append(s)
        return ok(s, 201)


@app.route('/specialities/<int:sid>', methods=['PUT'])
@require_token()
def update_speciality(sid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'specialities', 'edit'):
        return fail('You do not have permission to edit specialities', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    name = body.get('name')
    if not name:
        return fail('name is required', 400)
    if _use_db():
        r = query('UPDATE specialities SET name=%s WHERE id=%s RETURNING id, name', (name, sid))
        if not r:
            return fail('not found', 404)
        return ok(r[0])
    else:
        for s in _FALLBACK['specialities']:
            if s['id'] == sid:
                s['name'] = name
                return ok(s)
        return fail('not found', 404)


@app.route('/specialities/<int:sid>', methods=['DELETE'])
@require_token()
def delete_speciality(sid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'specialities', 'delete'):
        return fail('You do not have permission to delete specialities', 403)
    
    if _use_db():
        r = query('DELETE FROM specialities WHERE id=%s RETURNING id', (sid,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        for i, s in enumerate(_FALLBACK['specialities']):
            if s['id'] == sid:
                _FALLBACK['specialities'].pop(i)
                return ok({'deleted': sid})
        return fail('not found', 404)


# --- Patients endpoints --------------------------------------------------------
@app.route('/patients', methods=['GET'])
def list_patients():
    if _use_db():
        rows = query('SELECT id, first_name, last_name, email, phone FROM patients ORDER BY id LIMIT 200')
        return ok(rows)
    else:
        return ok([])


# --- Appointments endpoints ----------------------------------------------------
@app.route('/appointments', methods=['GET'])
@require_token()
def list_appointments():
    """List appointments - doctors see only their own, admin/office/nurse see all"""
    if _use_db():
        user = g.current_user
        # Simple appointment view joining patient and doctor names
        sql = '''
            SELECT a.id, a.appointment_date, a.start_time, a.end_time,
                   d.id as doctor_id, d.first_name as doctor_first, d.last_name as doctor_last,
                   p.id as patient_id, p.first_name as patient_first, p.last_name as patient_last,
                   a.status, a.prescription
            FROM appointments a
            LEFT JOIN doctors d ON d.id = a.doctor_id
            LEFT JOIN patients p ON p.id = a.patient_id
        '''
        # Doctor sees only their own appointments (based on doctor_id in users table)
        if user and user.get('role') == 'Doctor' and not user.get('is_admin'):
            if user.get('doctor_id'):
                sql += f" WHERE a.doctor_id={user.get('doctor_id')}"
        sql += ' ORDER BY a.appointment_date DESC, a.start_time DESC LIMIT 500'
        rows = query(sql)
        # Flatten doctor/patient names for the frontend
        for r in rows:
            r['doctor_name'] = f"{r.get('doctor_first') or ''} {r.get('doctor_last') or ''}".strip()
            r['patient_name'] = f"{r.get('patient_first') or ''} {r.get('patient_last') or ''}".strip()
        return ok(rows)
    else:
        return ok([])


@app.route('/appointments/<int:aid>', methods=['GET'])
@require_token()
def get_appointment(aid):
    """Get single appointment details"""
    if _use_db():
        user = g.current_user
        sql = '''
            SELECT a.id, a.appointment_date, a.start_time, a.end_time,
                   d.id as doctor_id, d.first_name as doctor_first, d.last_name as doctor_last,
                   p.id as patient_id, p.first_name as patient_first, p.last_name as patient_last,
                   a.status, a.prescription
            FROM appointments a
            LEFT JOIN doctors d ON d.id = a.doctor_id
            LEFT JOIN patients p ON p.id = a.patient_id
            WHERE a.id = %s
        '''
        rows = query(sql, (aid,))
        if not rows:
            return fail('not found', 404)
        
        appt = rows[0]
        
        # Doctor can only view their own appointments
        if user and user.get('role') == 'Doctor' and not user.get('is_admin'):
            if user.get('doctor_id') and appt.get('doctor_id') != user.get('doctor_id'):
                return fail('You can only view your own appointments', 403)
        
        # Flatten doctor/patient names
        appt['doctor_name'] = f"{appt.get('doctor_first') or ''} {appt.get('doctor_last') or ''}".strip()
        appt['patient_name'] = f"{appt.get('patient_first') or ''} {appt.get('patient_last') or ''}".strip()
        return ok(appt)
    else:
        return fail('not available without DB', 400)


# --- Doctors and schedules ---------------------------------------------------
@app.route('/doctors', methods=['GET'])
def list_doctors():
    if _use_db():
        rows = query('SELECT id, first_name, last_name, email, phone, speciality_id, registration_number FROM doctors ORDER BY id')
        return ok(rows)
    else:
        return ok([])


@app.route('/doctors/<int:did>', methods=['GET'])
def get_doctor(did):
    if _use_db():
        rows = query('SELECT id, first_name, last_name, email, phone, speciality_id, registration_number FROM doctors WHERE id=%s', (did,))
        if not rows:
            return fail('not found', 404)
        doctor = rows[0]
        schedules = query('SELECT id, doctor_id, day_of_week, start_time, end_time FROM doctor_schedules WHERE doctor_id=%s ORDER BY day_of_week, start_time', (did,))
        doctor['schedules'] = schedules
        return ok(doctor)
    else:
        return fail('not available without DB', 404)


@app.route('/doctors', methods=['POST'])
@require_token()
def create_doctor():
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'doctors', 'add'):
        return fail('You do not have permission to add doctors', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if not body.get('first_name') or not body.get('last_name'):
        return fail('first_name and last_name required', 400)
    if _use_db():
        r = query('INSERT INTO doctors (first_name, last_name, email, phone, speciality_id, registration_number) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, first_name, last_name, email, phone, speciality_id, registration_number',
                  (body.get('first_name'), body.get('last_name'), body.get('email'), body.get('phone'), body.get('speciality_id'), body.get('registration_number')))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)


@app.route('/doctors/<int:did>', methods=['PUT'])
@require_token()
def update_doctor(did):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'doctors', 'edit'):
        return fail('You do not have permission to edit doctors', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if _use_db():
        r = query('UPDATE doctors SET first_name=%s,last_name=%s,email=%s,phone=%s,speciality_id=%s,registration_number=%s WHERE id=%s RETURNING id, first_name, last_name, email, phone, speciality_id, registration_number',
                  (body.get('first_name'), body.get('last_name'), body.get('email'), body.get('phone'), body.get('speciality_id'), body.get('registration_number'), did))
        if not r:
            return fail('not found', 404)
        return ok(r[0])
    else:
        return fail('not available without DB', 404)


@app.route('/doctors/<int:did>', methods=['DELETE'])
@require_token()
def delete_doctor(did):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'doctors', 'delete'):
        return fail('You do not have permission to delete doctors', 403)
    
    if _use_db():
        # prevent deletion if doctor has pending appointments
        rows = query("SELECT count(*) as cnt FROM appointments WHERE doctor_id=%s AND status!='completed'", (did,))
        if rows and int(rows[0].get('cnt',0))>0:
            return fail('doctor has pending appointments', 400)
        r = query('DELETE FROM doctors WHERE id=%s RETURNING id', (did,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        return fail('not available without DB', 404)


@app.route('/doctors/<int:did>/schedules', methods=['POST'])
@require_token()
def add_schedule(did):
    body = request.get_json(force=True, silent=True) or {}
    dow = body.get('day_of_week')
    start = body.get('start_time')
    end = body.get('end_time')
    if dow is None or not start or not end:
        return fail('day_of_week, start_time and end_time required', 400)
    if _use_db():
        r = query('INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time) VALUES (%s,%s,%s,%s) RETURNING id, doctor_id, day_of_week, start_time, end_time',
                  (did, dow, start, end))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)


@app.route('/schedules/<int:sid>', methods=['PUT'])
@require_token()
def update_schedule(sid):
    body = request.get_json(force=True, silent=True) or {}
    dow = body.get('day_of_week')
    start = body.get('start_time')
    end = body.get('end_time')
    if dow is None or not start or not end:
        return fail('day_of_week, start_time and end_time required', 400)
    if _use_db():
        r = query('UPDATE doctor_schedules SET day_of_week=%s,start_time=%s,end_time=%s WHERE id=%s RETURNING id, doctor_id, day_of_week, start_time, end_time',
                  (dow, start, end, sid))
        if not r:
            return fail('not found', 404)
        return ok(r[0])
    else:
        return fail('not available without DB', 404)


@app.route('/schedules/<int:sid>', methods=['DELETE'])
@require_token()
def delete_schedule(sid):
    if _use_db():
        r = query('DELETE FROM doctor_schedules WHERE id=%s RETURNING id', (sid,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        return fail('not available without DB', 404)


# --- Availability and booking -----------------------------------------------
def _time_to_minutes(tstr):
    h, m, *rest = (tstr or '').split(':')
    return int(h) * 60 + int(m)


@app.route('/doctors/<int:did>/available_slots', methods=['GET'])
def available_slots(did):
    # params: date=YYYY-MM-DD, slot=minutes (default 10)
    date_str = request.args.get('date')
    slot = int(request.args.get('slot', '10'))
    if not date_str:
        return fail('date is required', 400)
    if not _use_db():
        return ok([])
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        return fail('invalid date', 400)
    dow = dt.weekday()  # 0=Monday
    # get schedules for that doctor and day
    schedules = query('SELECT id, start_time, end_time FROM doctor_schedules WHERE doctor_id=%s AND day_of_week=%s ORDER BY start_time', (did, dow))
    # get existing appointments for that date
    appts = query('SELECT start_time, end_time FROM appointments WHERE doctor_id=%s AND appointment_date=%s', (did, date_str))
    used = []
    for a in appts:
        used.append((a['start_time'], a['end_time']))
    slots = []
    for s in schedules:
        start_min = _time_to_minutes(s['start_time'])
        end_min = _time_to_minutes(s['end_time'])
        cur = start_min
        while cur + slot <= end_min:
            st = f"{cur//60:02d}:{cur%60:02d}:00"
            en = f"{(cur+slot)//60:02d}:{(cur+slot)%60:02d}:00"
            # check overlap with existing appts
            conflict = False
            for ustart, uend in used:
                um = _time_to_minutes(ustart)
                ue = _time_to_minutes(uend)
                if not (cur+slot <= um or cur >= ue):
                    conflict = True
                    break
            if not conflict:
                slots.append({'start_time': st, 'end_time': en})
            cur += slot
    return ok(slots)


@app.route('/appointments', methods=['POST'])
@require_token()
def create_appointment():
    """Create appointment - requires 'add' permission for appointments screen"""
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'appointments', 'add'):
        return fail('You do not have permission to add appointments', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    doctor_id = body.get('doctor_id')
    patient_id = body.get('patient_id')
    date_str = body.get('appointment_date')
    start_time = body.get('start_time')
    slot = int(body.get('slot_minutes', 10))
    if not doctor_id or not patient_id or not date_str or not start_time:
        return fail('doctor_id, patient_id, appointment_date and start_time are required', 400)
    if not _use_db():
        return fail('not available without DB', 400)
    # compute end_time
    sm = _time_to_minutes(start_time)
    em = sm + slot
    end_time = f"{em//60:02d}:{em%60:02d}:00"
    # check doctor schedule for that date
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        return fail('invalid appointment_date', 400)
    dow = dt.weekday()
    schedules = query('SELECT start_time, end_time FROM doctor_schedules WHERE doctor_id=%s AND day_of_week=%s', (doctor_id, dow))
    ok_slot = False
    for s in schedules:
        if _time_to_minutes(s['start_time']) <= sm and em <= _time_to_minutes(s['end_time']):
            ok_slot = True
            break
    if not ok_slot:
        return fail('slot not within doctor schedule', 400)
    # check overlapping appointments
    others = query('SELECT start_time, end_time FROM appointments WHERE doctor_id=%s AND appointment_date=%s', (doctor_id, date_str))
    for o in others:
        if not (em <= _time_to_minutes(o['start_time']) or sm >= _time_to_minutes(o['end_time'])):
            return fail('conflict with existing appointment', 400)
    # insert
    r = query('INSERT INTO appointments (doctor_id, patient_id, appointment_date, start_time, end_time, status) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, doctor_id, patient_id, appointment_date, start_time, end_time, status',
              (doctor_id, patient_id, date_str, start_time, end_time, 'booked'))
    return ok(r[0], 201)


@app.route('/appointments/<int:aid>', methods=['PUT'])
@require_token()
def update_appointment(aid):
    """Update appointment - doctors can update their own appointments with prescription details"""
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'appointments', 'edit'):
        return fail('You do not have permission to edit appointments', 403)
    
    if not _use_db():
        return fail('not available without DB', 400)
    
    body = request.get_json(force=True, silent=True) or {}
    
    # Get appointment to check ownership
    appt = query('SELECT id, doctor_id FROM appointments WHERE id=%s', (aid,))
    if not appt:
        return fail('not found', 404)
    
    # Doctor can only edit their own appointments
    if user.get('role') == 'Doctor' and not user.get('is_admin'):
        if user.get('doctor_id') and appt[0].get('doctor_id') != user.get('doctor_id'):
            return fail('You can only edit your own appointments', 403)
    
    # Update appointment fields (only prescription for doctors, more fields for admin)
    fields = []
    params = []
    
    if 'prescription' in body:
        fields.append('prescription=%s')
        params.append(body.get('prescription'))
    
    # Admin can update status
    if 'status' in body and user.get('is_admin'):
        fields.append('status=%s')
        params.append(body.get('status'))
    
    if not fields:
        return fail('no fields to update', 400)
    
    params.append(aid)
    sql = f"UPDATE appointments SET {', '.join(fields)} WHERE id=%s RETURNING id, appointment_date, start_time, end_time, doctor_id, patient_id, status, prescription"
    r = query(sql, tuple(params))
    if not r:
        return fail('not found', 404)
    return ok(r[0])


@app.route('/appointments/<int:aid>', methods=['DELETE'])
@require_token()
def delete_appointment(aid):
    """Delete appointment - requires 'delete' permission for appointments screen"""
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'appointments', 'delete'):
        return fail('You do not have permission to delete appointments', 403)
    
    if _use_db():
        # Get appointment to check doctor ownership
        appt = query('SELECT id, doctor_id FROM appointments WHERE id=%s', (aid,))
        if not appt:
            return fail('not found', 404)
        
        # Doctor can only delete their own appointments
        if user.get('role') == 'Doctor' and not user.get('is_admin'):
            if appt[0].get('doctor_id') != getattr(user, 'doctor_id', None):
                # Try to get doctor_id from user lookup
                user_row = query('SELECT role FROM users WHERE id=%s', (user.get('id'),))
                if user_row and user_row[0].get('role') == 'Doctor':
                    # For now, restrict (in production, map user to doctor)
                    return fail('You can only delete your own appointments', 403)
        
        r = query('DELETE FROM appointments WHERE id=%s RETURNING id', (aid,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        return fail('not available without DB', 400)


# --- Patients CRUD ----------------------------------------------------------
@app.route('/patients/<int:pid>', methods=['GET'])
def get_patient(pid):
    if _use_db():
        rows = query('SELECT id, first_name, last_name, email, phone FROM patients WHERE id=%s', (pid,))
        if not rows:
            return fail('not found', 404)
        return ok(rows[0])
    else:
        return fail('not available without DB', 404)


@app.route('/patients', methods=['POST'])
@require_token()
def create_patient():
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'patients', 'add'):
        return fail('You do not have permission to add patients', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if not body.get('first_name') or not body.get('last_name'):
        return fail('first_name and last_name required', 400)
    if _use_db():
        r = query('INSERT INTO patients (first_name,last_name,email,phone) VALUES (%s,%s,%s,%s) RETURNING id, first_name, last_name, email, phone',
                  (body.get('first_name'), body.get('last_name'), body.get('email'), body.get('phone')))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)



@app.route('/patients/<int:pid>', methods=['PUT'])
@require_token()
def update_patient(pid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'patients', 'edit'):
        return fail('You do not have permission to edit patients', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if _use_db():
        r = query('UPDATE patients SET first_name=%s,last_name=%s,email=%s,phone=%s WHERE id=%s RETURNING id, first_name, last_name, email, phone',
                  (body.get('first_name'), body.get('last_name'), body.get('email'), body.get('phone'), pid))
        if not r:
            return fail('not found', 404)
        return ok(r[0])
    else:
        return fail('not available without DB', 404)


@app.route('/patients/<int:pid>', methods=['DELETE'])
@require_token()
def delete_patient(pid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'patients', 'delete'):
        return fail('You do not have permission to delete patients', 403)
    
    if _use_db():
        rows = query("SELECT count(*) as cnt FROM appointments WHERE patient_id=%s AND status!='completed'", (pid,))
        if rows and int(rows[0].get('cnt',0))>0:
            return fail('patient has pending appointments', 400)
        r = query('DELETE FROM patients WHERE id=%s RETURNING id', (pid,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        return fail('not available without DB', 404)


# --- Schedules list across doctors -----------------------------------------
@app.route('/schedules', methods=['GET'])
def list_schedules():
    if _use_db():
        rows = query('SELECT id, doctor_id, day_of_week, start_time, end_time FROM doctor_schedules ORDER BY doctor_id, day_of_week, start_time')
        return ok(rows)
    else:
        return ok([])


# --- Leaves (doctor leaves) -------------------------------------------------
@app.route('/leaves', methods=['GET'])
def list_leaves():
    if _use_db():
        rows = query('SELECT id, doctor_id, leave_date, reason FROM doctor_leaves ORDER BY leave_date DESC')
        return ok(rows)
    else:
        return ok([])


@app.route('/leaves', methods=['POST'])
@require_token()
def create_leave():
    body = request.get_json(force=True, silent=True) or {}
    if not body.get('doctor_id') or not body.get('leave_date'):
        return fail('doctor_id and leave_date required', 400)
    if _use_db():
        r = query('INSERT INTO doctor_leaves (doctor_id, leave_date, reason) VALUES (%s,%s,%s) RETURNING id, doctor_id, leave_date, reason',
                  (body.get('doctor_id'), body.get('leave_date'), body.get('reason')))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)


@app.route('/leaves/<int:lid>', methods=['DELETE'])
@require_token()
def delete_leave(lid):
    if _use_db():
        r = query('DELETE FROM doctor_leaves WHERE id=%s RETURNING id', (lid,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        return fail('not available without DB', 404)


# --- Case history for patients ---------------------------------------------
@app.route('/case_histories', methods=['GET'])
def list_case_histories():
    pid = request.args.get('patient_id')
    if _use_db():
        if pid:
            rows = query('SELECT id, patient_id, notes, created_at FROM case_histories WHERE patient_id=%s ORDER BY created_at DESC', (pid,))
        else:
            rows = query('SELECT id, patient_id, notes, created_at FROM case_histories ORDER BY created_at DESC LIMIT 500')
        return ok(rows)
    else:
        return ok([])


@app.route('/case_histories', methods=['POST'])
@require_token()
def create_case_history():
    body = request.get_json(force=True, silent=True) or {}
    if not body.get('patient_id') or not body.get('notes'):
        return fail('patient_id and notes required', 400)
    if _use_db():
        r = query('INSERT INTO case_histories (patient_id, notes, created_at) VALUES (%s,%s,now()) RETURNING id, patient_id, notes, created_at',
                  (body.get('patient_id'), body.get('notes')))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)


@app.route('/case_histories/<int:cid>', methods=['DELETE'])
@require_token()
def delete_case_history(cid):
    if _use_db():
        r = query('DELETE FROM case_histories WHERE id=%s RETURNING id', (cid,))
        if not r:
            return fail('not found', 404)
        return ok({'deleted': r[0]['id']})
    else:
        return fail('not available without DB', 404)


# --- Reports: simple financial summary -------------------------------------
@app.route('/reports/financial', methods=['GET'])
@require_token(role='Billing')
def financial_report():
    # month in YYYY-MM
    month = request.args.get('month')
    fee = float(os.getenv('APPT_FEE', '100'))
    cost_pct = float(os.getenv('COST_PCT', '0.3'))
    if not _use_db():
        return ok({'month': month, 'revenue': 0.0, 'costs': 0.0, 'profit': 0.0})
    if not month:
        return fail('month is required (YYYY-MM)', 400)
    try:
        y, m = month.split('-')
        y = int(y); m = int(m)
    except Exception:
        return fail('invalid month', 400)
    start = f"{y:04d}-{m:02d}-01"
    # naive month end (not handling month lengths specially, use SQL date_trunc)
    sql = "SELECT count(*) as cnt FROM appointments WHERE to_char(appointment_date,'YYYY-MM')=%s"
    rows = query(sql, (month,))
    cnt = int(rows[0]['cnt']) if rows else 0
    revenue = cnt * fee
    costs = revenue * cost_pct
    profit = revenue - costs
    return ok({'month': month, 'appointments': cnt, 'revenue': revenue, 'costs': costs, 'profit': profit})


# --- Billing transactions CRUD ----------------------------------------------
@app.route('/billing/transactions', methods=['GET'])
@require_token()
def list_billing_transactions():
    # filters: start, end
    start = request.args.get('start')
    typ = request.args.get('type')
    end = request.args.get('end')
    if not _use_db():
        return ok([])
    sql = 'SELECT bt.id, bt.trans_date, bt.amount, bt.type, c.name as category, bt.description, bt.created_at FROM billing_transactions bt LEFT JOIN billing_categories c ON bt.category_id=c.id'
    params = []
    clauses = []
    if start and end:
        clauses.append('bt.trans_date BETWEEN %s AND %s')
        params.extend([start, end])
    if typ:
        clauses.append('bt.type=%s')
        params.append(typ)
    if clauses:
        sql += ' WHERE ' + ' AND '.join(clauses)
    sql += ' ORDER BY bt.trans_date DESC'
    rows = query(sql, tuple(params) if params else None)
    return ok(rows)


@app.route('/billing/transactions', methods=['POST'])
@require_token()
def create_billing_transaction():
    body = request.get_json(force=True, silent=True) or {}
    if not body.get('trans_date') or not body.get('amount') or not body.get('type'):
        return fail('trans_date, amount, type required', 400)
    if body.get('type') not in ('income','expense'):
        return fail('invalid type', 400)
    cat = body.get('category_id')
    created_by = g.current_user.get('id') if getattr(g, 'current_user', None) else None
    if _use_db():
        r = query('INSERT INTO billing_transactions (trans_date, amount, type, category_id, description, created_by) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, trans_date, amount, type, category_id, description, created_at',
                  (body.get('trans_date'), body.get('amount'), body.get('type'), cat, body.get('description'), created_by))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)


@app.route('/billing/transactions/<int:tid>', methods=['PUT'])
@require_token()
def update_billing_transaction(tid):
    body = request.get_json(force=True, silent=True) or {}
    if not _use_db():
        return fail('not available without DB', 400)
    fields = []
    params = []
    for k in ('trans_date','amount','type','category_id','description'):
        if k in body:
            fields.append(f"{k}=%s")
            params.append(body.get(k))
    if not fields:
        return fail('no fields provided', 400)
    params.append(tid)
    sql = f"UPDATE billing_transactions SET {', '.join(fields)} WHERE id=%s RETURNING id, trans_date, amount, type, category_id, description, created_at"
    r = query(sql, tuple(params))
    if not r:
        return fail('not found', 404)
    return ok(r[0])


@app.route('/billing/transactions/<int:tid>', methods=['DELETE'])
@require_token()
def delete_billing_transaction(tid):
    if not _use_db():
        return fail('not available without DB', 400)
    r = query('DELETE FROM billing_transactions WHERE id=%s RETURNING id', (tid,))
    if not r:
        return fail('not found', 404)
    return ok({'deleted': r[0]['id']})


# --- Billing reports / dashboard -------------------------------------------
@app.route('/reports/billing', methods=['GET'])
@require_token(role='Billing')
def billing_report():
    # params: period=YYYY-MM or year=YYYY ; format=csv|xls|pdf
    period = request.args.get('period')
    year = request.args.get('year')
    fmt = request.args.get('format', 'json')
    if not _use_db():
        return ok({'income':0.0,'expenses':0.0,'profit':0.0,'by_month':[]})
    if period:
        # monthly
        sql = "SELECT type, sum(amount) as total FROM billing_transactions WHERE to_char(trans_date,'YYYY-MM')=%s GROUP BY type"
        rows = query(sql, (period,))
        income = sum(r['total'] for r in rows if r['type']=='income')
        expenses = sum(r['total'] for r in rows if r['type']=='expense')
        profit = income - expenses
        result = {'period': period, 'income': income, 'expenses': expenses, 'profit': profit}
        if fmt in ('csv','xls','pdf'):
            trows = query('SELECT trans_date, amount, type, description FROM billing_transactions WHERE to_char(trans_date,\'YYYY-MM\')=%s ORDER BY trans_date', (period,))
            return export_transactions(trows, fmt, f'billing_{period}')
        return ok(result)
    elif year:
        sql = "SELECT to_char(trans_date,'YYYY-MM') as month, type, sum(amount) as total FROM billing_transactions WHERE to_char(trans_date,'YYYY')=%s GROUP BY month, type ORDER BY month"
        rows = query(sql, (year,))
        by_month = {}
        for r in rows:
            m = r['month']
            by_month.setdefault(m, {'income':0.0,'expenses':0.0})
            if r['type']=='income':
                by_month[m]['income'] += r['total']
            else:
                by_month[m]['expenses'] += r['total']
        months = []
        for m in sorted(by_month.keys()):
            inc = by_month[m]['income']
            exp = by_month[m]['expenses']
            months.append({'month': m, 'income': inc, 'expenses': exp, 'profit': inc-exp})
        result = {'year': year, 'by_month': months}
        if fmt in ('csv','xls','pdf'):
            trows = [{'period': x['month'], 'income': x['income'], 'expenses': x['expenses'], 'profit': x['profit']} for x in months]
            return export_aggregates(trows, fmt, f'billing_{year}')
        return ok(result)
    else:
        return fail('period (YYYY-MM) or year (YYYY) required', 400)


def export_transactions(rows, fmt, basename):
    if fmt == 'csv' or fmt == 'xls':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['trans_date','amount','type','description'])
        for r in rows:
            writer.writerow([r.get('trans_date'), r.get('amount'), r.get('type'), r.get('description')])
        data = output.getvalue().encode('utf-8')
        fname = f"{basename}.{ 'xls' if fmt=='xls' else 'csv' }"
        return send_file(io.BytesIO(data), as_attachment=True, download_name=fname, mimetype='text/csv')
    elif fmt == 'pdf':
        try:
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
        except Exception:
            return fail('PDF export not available: install reportlab', 500)
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        data = [['Date','Amount','Type','Description']]
        for r in rows:
            data.append([r.get('trans_date'), str(r.get('amount')), r.get('type'), r.get('description') or ''])
        table = Table(data, colWidths=[80,60,60,260])
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.5,colors.black)]))
        doc.build([table])
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"{basename}.pdf", mimetype='application/pdf')
    else:
        return fail('unsupported format', 400)


def export_aggregates(rows, fmt, basename):
    if fmt in ('csv','xls'):
        output = io.StringIO()
        writer = csv.writer(output)
        keys = list(rows[0].keys()) if rows else ['period','income','expenses','profit']
        writer.writerow(keys)
        for r in rows:
            writer.writerow([r.get(k) for k in keys])
        data = output.getvalue().encode('utf-8')
        fname = f"{basename}.{ 'xls' if fmt=='xls' else 'csv' }"
        return send_file(io.BytesIO(data), as_attachment=True, download_name=fname, mimetype='text/csv')
    elif fmt == 'pdf':
        try:
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
        except Exception:
            return fail('PDF export not available: install reportlab', 500)
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        if rows:
            keys = list(rows[0].keys())
        else:
            keys = ['period','income','expenses','profit']
        data = [keys]
        for r in rows:
            data.append([r.get(k) for k in keys])
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.5,colors.black)]))
        doc.build([table])
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"{basename}.pdf", mimetype='application/pdf')
    else:
        return fail('unsupported format', 400)


# --- Invoices and payments API ---------------------------------------------
@app.route('/invoices', methods=['GET'])
@require_token(roles=['Billing','Admin'])
def list_invoices():
    if not _use_db():
        return ok([])
    patient_id = request.args.get('patient_id')
    sql = 'SELECT id, invoice_no, patient_id, doctor_id, invoice_date, total, status, created_at FROM invoices'
    params = []
    if patient_id:
        sql += ' WHERE patient_id=%s'
        params = [patient_id]
    sql += ' ORDER BY invoice_date DESC'
    rows = query(sql, tuple(params) if params else None)
    return ok(rows)


@app.route('/invoices', methods=['POST'])
@require_token(roles=['Billing','Admin'])
def create_invoice():
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'invoices', 'add'):
        return fail('You do not have permission to add invoices', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    lines = body.get('lines', [])
    invoice_date = body.get('invoice_date') or datetime.utcnow().date().isoformat()
    if not _use_db():
        return fail('DB required', 400)
    r = query('INSERT INTO invoices (invoice_no, patient_id, doctor_id, invoice_date, status, created_by) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id',
              (body.get('invoice_no'), body.get('patient_id'), body.get('doctor_id'), invoice_date, body.get('status','draft'), g.current_user.get('id') if getattr(g,'current_user',None) else None))
    iid = r[0]['id']
    total = 0
    for ln in lines:
        desc = ln.get('description')
        qty = int(ln.get('qty') or 1)
        up = float(ln.get('unit_price') or 0)
        amt = qty * up
        total += amt
        query('INSERT INTO invoice_lines (invoice_id, description, qty, unit_price, amount) VALUES (%s,%s,%s,%s,%s)', (iid, desc, qty, up, amt))
    query('UPDATE invoices SET total=%s WHERE id=%s', (total, iid))
    # generate invoice_no if missing: INV-YYYYMM-<id>
    invrow = query('SELECT invoice_no, invoice_date FROM invoices WHERE id=%s', (iid,))
    invrow = invrow[0]
    if not invrow.get('invoice_no'):
        try:
            idate = datetime.fromisoformat(str(invrow.get('invoice_date'))).date()
        except Exception:
            idate = datetime.utcnow().date()
        num = f"INV-{idate.year}{idate.month:02d}-{iid}"
        query('UPDATE invoices SET invoice_no=%s WHERE id=%s', (num, iid))
    inv = query('SELECT id, invoice_no, patient_id, doctor_id, invoice_date, total, status, created_at FROM invoices WHERE id=%s', (iid,))
    return ok(inv[0], 201)


@app.route('/invoices/<int:iid>', methods=['GET'])
@require_token(roles=['Billing','Admin'])
def get_invoice(iid):
    if not _use_db():
        return fail('DB required', 400)
    inv = query('SELECT id, invoice_no, patient_id, doctor_id, invoice_date, total, status, created_at FROM invoices WHERE id=%s', (iid,))
    if not inv:
        return fail('not found', 404)
    lines = query('SELECT id, description, qty, unit_price, amount FROM invoice_lines WHERE invoice_id=%s', (iid,))
    inv = inv[0]
    inv['lines'] = lines
    payments = query('SELECT id, amount, payment_date, method, reference, created_at FROM payments WHERE invoice_id=%s ORDER BY payment_date', (iid,))
    inv['payments'] = payments
    # compute outstanding
    paid = sum(p.get('amount', 0) for p in payments) if payments else 0
    inv['paid'] = paid
    inv['outstanding'] = float(inv.get('total') or 0) - paid
    return ok(inv)


@app.route('/invoices/<int:iid>', methods=['PUT'])
@require_token(roles=['Billing','Admin'])
def update_invoice(iid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'invoices', 'edit'):
        return fail('You do not have permission to edit invoices', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if not _use_db():
        return fail('DB required', 400)
    fields = []
    params = []
    for k in ('invoice_no','patient_id','doctor_id','invoice_date','status'):
        if k in body:
            fields.append(f"{k}=%s")
            params.append(body.get(k))
    if fields:
        params.append(iid)
        sql = f"UPDATE invoices SET {', '.join(fields)} WHERE id=%s RETURNING id, invoice_no, patient_id, doctor_id, invoice_date, total, status, created_at"
        r = query(sql, tuple(params))
        if not r:
            return fail('not found', 404)
        return ok(r[0])
    return fail('no fields', 400)


@app.route('/invoices/<int:iid>', methods=['DELETE'])
@require_token(roles=['Billing','Admin'])
def delete_invoice(iid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'invoices', 'delete'):
        return fail('You do not have permission to delete invoices', 403)
    
    if not _use_db():
        return fail('DB required', 400)
    r = query('DELETE FROM invoices WHERE id=%s RETURNING id', (iid,))
    if not r:
        return fail('not found', 404)
    return ok({'deleted': r[0]['id']})


@app.route('/invoices/<int:iid>/lines', methods=['POST'])
@require_token(roles=['Billing','Admin'])
def add_invoice_line(iid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'invoices', 'add'):
        return fail('You do not have permission to add invoice lines', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if not _use_db():
        return fail('DB required', 400)
    qty = int(body.get('qty') or 1)
    up = float(body.get('unit_price') or 0)
    amt = qty * up
    r = query('INSERT INTO invoice_lines (invoice_id, description, qty, unit_price, amount) VALUES (%s,%s,%s,%s,%s) RETURNING id', (iid, body.get('description'), qty, up, amt))
    # update invoice total
    query('UPDATE invoices SET total = (SELECT COALESCE(SUM(amount),0) FROM invoice_lines WHERE invoice_id=%s) WHERE id=%s', (iid, iid))
    return ok(r[0], 201)


@app.route('/payments', methods=['GET'])
@require_token(roles=['Billing','Admin'])
def list_payments():
    if not _use_db():
        return ok([])
    sql = 'SELECT id, invoice_id, amount, payment_date, method, reference, created_at FROM payments ORDER BY payment_date DESC'
    rows = query(sql)
    return ok(rows)


@app.route('/payments', methods=['POST'])
@require_token(roles=['Billing','Admin'])
def create_payment():
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'transactions', 'add'):
        return fail('You do not have permission to add payments', 403)
    
    body = request.get_json(force=True, silent=True) or {}
    if not _use_db():
        return fail('DB required', 400)
    iid = body.get('invoice_id')
    amt = float(body.get('amount') or 0)
    pdate = body.get('payment_date') or datetime.utcnow().date().isoformat()
    r = query('INSERT INTO payments (invoice_id, amount, payment_date, method, reference, created_by) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id', (iid, amt, pdate, body.get('method'), body.get('reference'), g.current_user.get('id') if getattr(g,'current_user',None) else None))
    # update invoice total/payments not reconciling here
    # optionally update invoice status if fully paid
    try:
        inv = query('SELECT total FROM invoices WHERE id=%s', (iid,))
        if inv:
            total = float(inv[0].get('total') or 0)
            paid = query('SELECT COALESCE(SUM(amount),0) as paid FROM payments WHERE invoice_id=%s', (iid,))[0].get('paid')
            paid = float(paid or 0)
            if paid >= total and total > 0:
                query('UPDATE invoices SET status=%s WHERE id=%s', ('paid', iid))
    except Exception:
        pass
    return ok(r[0], 201)


@app.route('/payments/<int:pid>', methods=['DELETE'])
@require_token(roles=['Billing','Admin'])
def delete_payment(pid):
    user = g.current_user
    # Check action permission
    if not can_perform_action(user, 'transactions', 'delete'):
        return fail('You do not have permission to delete payments', 403)
    
    if not _use_db():
        return fail('DB required', 400)
    r = query('DELETE FROM payments WHERE id=%s RETURNING id', (pid,))
    if not r:
        return fail('not found', 404)
    # if payment removed, ensure invoice status adjusted
    try:
        # find invoice id from deleted row? we don't have it; skip
        pass
    except Exception:
        pass
    return ok({'deleted': r[0]['id']})


@app.route('/invoices/<int:iid>/export', methods=['GET'])
@require_token(roles=['Billing','Admin'])
def export_invoice_pdf(iid):
    if not _use_db():
        return fail('DB required', 400)
    inv = query('SELECT id, invoice_no, patient_id, doctor_id, invoice_date, total, status, created_at FROM invoices WHERE id=%s', (iid,))
    if not inv:
        return fail('not found', 404)
    inv = inv[0]
    lines = query('SELECT description, qty, unit_price, amount FROM invoice_lines WHERE invoice_id=%s', (iid,))
    payments = query('SELECT amount, payment_date, method, reference FROM payments WHERE invoice_id=%s ORDER BY payment_date', (iid,))
    paid = sum(p.get('amount',0) for p in payments) if payments else 0
    outstanding = float(inv.get('total') or 0) - paid
    # build PDF using reportlab
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception:
        return fail('PDF export not available: install reportlab', 500)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elems = []
    elems.append(Paragraph(f"Invoice: {inv.get('invoice_no')}", styles['Title']))
    elems.append(Spacer(1,6))
    elems.append(Paragraph(f"Date: {inv.get('invoice_date')}", styles['Normal']))
    elems.append(Paragraph(f"Status: {inv.get('status')}", styles['Normal']))
    elems.append(Spacer(1,12))
    # lines table
    data = [['Description','Qty','Unit','Amount']]
    for l in lines:
        data.append([l.get('description') or '', str(l.get('qty') or ''), str(l.get('unit_price') or ''), str(l.get('amount') or '')])
    data.append(['','', 'Total', str(inv.get('total'))])
    t = Table(data, colWidths=[250,40,60,70])
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
    elems.append(t)
    elems.append(Spacer(1,12))
    # payments
    paydata = [['Payment Date','Amount','Method','Reference']]
    for p in payments:
        paydata.append([str(p.get('payment_date') or ''), str(p.get('amount') or ''), p.get('method') or '', p.get('reference') or ''])
    paydata.append(['','', 'Paid', str(paid)])
    paydata.append(['','', 'Outstanding', str(outstanding)])
    pt = Table(paydata, colWidths=[100,80,120,120])
    pt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
    elems.append(pt)
    doc.build(elems)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"{inv.get('invoice_no')}.pdf", mimetype='application/pdf')


# --- Run block -----------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv('API_PORT', '8004'))
    host = os.getenv('API_HOST', '0.0.0.0')
    # Use threaded server for simple dev concurrency
    app.run(host=host, port=port, threaded=True)
