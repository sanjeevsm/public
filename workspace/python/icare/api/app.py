import os
import io
import csv
import json
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from flask import Flask, request, jsonify, send_file
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

# --- Specialities endpoints -----------------------------------------------------
@app.route('/specialities', methods=['GET'])
def list_specialities():
    if _use_db():
        rows = query('SELECT id, name FROM specialities ORDER BY id')
        return ok(rows)
    else:
        return ok(_FALLBACK['specialities'])


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
def create_speciality():
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
def update_speciality(sid):
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
def delete_speciality(sid):
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


# --- Run block -----------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv('API_PORT', '8004'))
    host = os.getenv('API_HOST', '0.0.0.0')
    # Use threaded server for simple dev concurrency
    app.run(host=host, port=port, threaded=True)
