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

# (rest identical to original app.py)
