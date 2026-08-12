import os
import io
import csv
import json
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from flask import Flask, request, jsonify, send_file
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
def list_appointments():
    if _use_db():
        # Simple appointment view joining patient and doctor names
        sql = '''
            SELECT a.id, a.appointment_date, a.start_time, a.end_time,
                   d.id as doctor_id, d.first_name as doctor_first, d.last_name as doctor_last,
                   p.id as patient_id, p.first_name as patient_first, p.last_name as patient_last,
                   a.status
            FROM appointments a
            LEFT JOIN doctors d ON d.id = a.doctor_id
            LEFT JOIN patients p ON p.id = a.patient_id
            ORDER BY a.appointment_date DESC, a.start_time DESC
            LIMIT 500
        '''
        rows = query(sql)
        # Flatten doctor/patient names for the frontend
        for r in rows:
            r['doctor_name'] = f"{r.get('doctor_first') or ''} {r.get('doctor_last') or ''}".strip()
            r['patient_name'] = f"{r.get('patient_first') or ''} {r.get('patient_last') or ''}".strip()
        return ok(rows)
    else:
        return ok([])


# --- Doctors and schedules ---------------------------------------------------
@app.route('/doctors', methods=['GET'])
def list_doctors():
    if _use_db():
        rows = query('SELECT id, first_name, last_name, email, phone, speciality_id FROM doctors ORDER BY id')
        return ok(rows)
    else:
        return ok([])


@app.route('/doctors/<int:did>', methods=['GET'])
def get_doctor(did):
    if _use_db():
        rows = query('SELECT id, first_name, last_name, email, phone, speciality_id FROM doctors WHERE id=%s', (did,))
        if not rows:
            return fail('not found', 404)
        doctor = rows[0]
        schedules = query('SELECT id, doctor_id, day_of_week, start_time, end_time FROM doctor_schedules WHERE doctor_id=%s ORDER BY day_of_week, start_time', (did,))
        doctor['schedules'] = schedules
        return ok(doctor)
    else:
        return fail('not available without DB', 404)


@app.route('/doctors', methods=['POST'])
def create_doctor():
    body = request.get_json(force=True, silent=True) or {}
    if not body.get('first_name') or not body.get('last_name'):
        return fail('first_name and last_name required', 400)
    if _use_db():
        r = query('INSERT INTO doctors (first_name, last_name, email, phone, speciality_id) VALUES (%s,%s,%s,%s,%s) RETURNING id, first_name, last_name, email, phone, speciality_id',
                  (body.get('first_name'), body.get('last_name'), body.get('email'), body.get('phone'), body.get('speciality_id')))
        return ok(r[0], 201)
    else:
        return fail('not available without DB', 400)


@app.route('/doctors/<int:did>', methods=['PUT'])
def update_doctor(did):
    body = request.get_json(force=True, silent=True) or {}
    if _use_db():
        r = query('UPDATE doctors SET first_name=%s,last_name=%s,email=%s,phone=%s,speciality_id=%s WHERE id=%s RETURNING id, first_name, last_name, email, phone, speciality_id',
                  (body.get('first_name'), body.get('last_name'), body.get('email'), body.get('phone'), body.get('speciality_id'), did))
        if not r:
            return fail('not found', 404)
        return ok(r[0])
    else:
        return fail('not available without DB', 404)


@app.route('/doctors/<int:did>', methods=['DELETE'])
def delete_doctor(did):
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
def create_appointment():
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
def create_patient():
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
def update_patient(pid):
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
def delete_patient(pid):
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

# --- Run block -----------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.getenv('API_PORT', '8004'))
    host = os.getenv('API_HOST', '0.0.0.0')
    # Use threaded server for simple dev concurrency
    app.run(host=host, port=port, threaded=True)
