"""Minimal Flask web frontend for iCare+ (serves templates and proxies simple API calls).
Uses `API_URL` environment variable (default http://localhost:8004).
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
from flask import session, flash, make_response
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, template_folder='.')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.getenv('WEB_SECRET', 'dev-secret')
API_URL = os.getenv('API_URL', 'http://localhost:8004')
API_TIMEOUT = 10
# White-label branding: text shown in the app badge/logo. Override via BRAND_NAME.
BRAND_NAME = os.getenv('BRAND_NAME', 'iCare+')


def api_headers():
    h = {}
    if session.get('token'):
        h['Authorization'] = f"Bearer {session.get('token')}"
    return h


def _api_error(resp):
    """Extract a human-readable error message from an API response."""
    try:
        data = resp.json()
        return data.get('error') or data.get('message') or f'Request failed ({resp.status_code})'
    except Exception:
        return f'Request failed ({resp.status_code})'


def api_get(path, params=None, default=None):
    """GET from the API. On any failure, flash a message and return `default`
    so pages render gracefully instead of raising a 500."""
    try:
        r = requests.get(f'{API_URL}{path}', params=params, headers=api_headers(), timeout=API_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        flash(_api_error(r), 'danger')
    except requests.exceptions.RequestException:
        flash('Cannot reach the API server — is it running?', 'danger')
    return default


def api_send(method, path, json=None, ok_codes=(200, 201), success=None, error=None):
    """POST/PUT/DELETE to the API with consistent success/error flashing.
    Returns (ok: bool, data: parsed-json-or-None)."""
    try:
        r = requests.request(method, f'{API_URL}{path}', json=json, headers=api_headers(), timeout=API_TIMEOUT)
        if r.status_code in ok_codes:
            if success:
                flash(success, 'success')
            try:
                return True, r.json()
            except Exception:
                return True, None
        flash(error or _api_error(r), 'danger')
    except requests.exceptions.RequestException:
        flash('Cannot reach the API server — is it running?', 'danger')
    return False, None


@app.context_processor
def inject_api_url():
    return dict(api_url=API_URL, brand_name=BRAND_NAME)


@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Clear any stale flash messages (e.g., from previous logout)
        session.pop('_flashes', None)
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        r = requests.post(f'{API_URL}/auth/login', json={'username': username, 'password': password}, timeout=API_TIMEOUT)
        if r.status_code == 200:
            payload = r.json()
            session['user'] = payload.get('user') or payload
            session['token'] = payload.get('token')
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        flash(_api_error(r) if r.text else 'Login failed', 'danger')
    except requests.exceptions.RequestException:
        flash('Cannot reach the API server — is it running?', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('token', None)
    flash('Logged out', 'info')
    return redirect(url_for('index'))


# --- Specialities -----------------------------------------------------------
@app.route('/specialities')
def specialities():
    return render_template('specialities.html', specialities=api_get('/specialities', default=[]))


@app.route('/specialities/new')
def new_speciality():
    return render_template('specialities_edit.html', speciality=None, action=url_for('create_speciality'))


@app.route('/specialities', methods=['POST'])
def create_speciality():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('specialities'))
    api_send('POST', '/specialities', json={'name': name}, success='Speciality created')
    return redirect(url_for('specialities'))


@app.route('/specialities/<int:sid>/edit')
def edit_speciality(sid):
    sp = api_get(f'/specialities/{sid}')
    if sp is None:
        return redirect(url_for('specialities'))
    return render_template('specialities_edit.html', speciality=sp, action=url_for('update_speciality', sid=sid))


@app.route('/specialities/<int:sid>', methods=['POST'])
def update_speciality(sid):
    name = request.form.get('name')
    if name:
        api_send('PUT', f'/specialities/{sid}', json={'name': name}, success='Speciality updated')
    return redirect(url_for('specialities'))


@app.route('/specialities/<int:sid>/delete', methods=['POST'])
def delete_speciality(sid):
    api_send('DELETE', f'/specialities/{sid}', success='Speciality deleted')
    return redirect(url_for('specialities'))


# --- Patients ---------------------------------------------------------------
@app.route('/patients')
def patients():
    return render_template('patients.html', patients=api_get('/patients', default=[]))


@app.route('/patients/new')
def new_patient():
    return render_template('patients_edit.html', patient=None, action=url_for('create_patient'))


@app.route('/patients', methods=['POST'])
def create_patient():
    data = {k: request.form.get(k) for k in ('first_name', 'last_name', 'email', 'phone')}
    api_send('POST', '/patients', json=data, success='Patient created')
    return redirect(url_for('patients'))


@app.route('/patients/<int:pid>/edit')
def edit_patient(pid):
    p = api_get(f'/patients/{pid}')
    if p is None:
        return redirect(url_for('patients'))
    return render_template('patients_edit.html', patient=p, action=url_for('update_patient', pid=pid))


@app.route('/patients/<int:pid>', methods=['POST'])
def update_patient(pid):
    data = {k: request.form.get(k) for k in ('first_name', 'last_name', 'email', 'phone')}
    api_send('PUT', f'/patients/{pid}', json=data, success='Patient updated')
    return redirect(url_for('patients'))


@app.route('/patients/<int:pid>/delete', methods=['POST'])
def delete_patient(pid):
    api_send('DELETE', f'/patients/{pid}', success='Patient deleted')
    return redirect(url_for('patients'))


# --- Schedules / Leaves / Case history --------------------------------------
@app.route('/schedules')
def schedules():
    return render_template('schedules.html')


@app.route('/leaves')
def leaves():
    return render_template('leaves.html')


@app.route('/leaves/new', methods=['POST'])
def create_leave_route():
    data = {'doctor_id': int(request.form.get('doctor_id')), 'leave_date': request.form.get('leave_date'), 'reason': request.form.get('reason')}
    api_send('POST', '/leaves', json=data, success='Leave recorded')
    return redirect(url_for('leaves'))


@app.route('/leaves/<int:lid>/delete', methods=['POST'])
def delete_leave_route(lid):
    api_send('DELETE', f'/leaves/{lid}', success='Leave deleted')
    return redirect(url_for('leaves'))


@app.route('/case_history')
def case_history():
    return render_template('case_history.html')


@app.route('/case_histories/new', methods=['POST'])
def create_case_history_route():
    data = {'patient_id': int(request.form.get('patient_id')), 'notes': request.form.get('notes')}
    api_send('POST', '/case_histories', json=data, success='Note added')
    return redirect(url_for('case_history'))


@app.route('/case_histories/<int:cid>/delete', methods=['POST'])
def delete_case_history_route(cid):
    api_send('DELETE', f'/case_histories/{cid}', success='Note deleted')
    return redirect(url_for('case_history'))


# --- Doctors ----------------------------------------------------------------
@app.route('/doctors')
def doctors():
    docs = api_get('/doctors', default=[])
    specs = api_get('/specialities', default=[])
    spec_map = {item.get('id'): item.get('name') for item in specs}
    return render_template('doctors.html', doctors=docs, specialities=spec_map)


@app.route('/doctors/new')
def new_doctor():
    return render_template('doctors_edit.html', doctor=None, action=url_for('create_doctor'))


@app.route('/doctors', methods=['POST'])
def create_doctor():
    data = {k: request.form.get(k) for k in ('first_name', 'last_name', 'email', 'phone', 'speciality_id', 'registration_number')}
    ok, doc = api_send('POST', '/doctors', json=data, success='Doctor created')
    if ok and doc:
        # collect schedules from form arrays
        days = request.form.getlist('schedule_day[]') if 'schedule_day[]' in request.form else request.form.getlist('schedule_day')
        starts = request.form.getlist('schedule_start[]') if 'schedule_start[]' in request.form else request.form.getlist('schedule_start')
        ends = request.form.getlist('schedule_end[]') if 'schedule_end[]' in request.form else request.form.getlist('schedule_end')
        for i in range(len(days)):
            try:
                dow = int(days[i])
            except (ValueError, TypeError):
                continue
            st = starts[i] if i < len(starts) else ''
            en = ends[i] if i < len(ends) else ''
            if st and en:
                if len(st.split(':')) == 2:
                    st = st + ':00'
                if len(en.split(':')) == 2:
                    en = en + ':00'
                api_send('POST', f"/doctors/{doc['id']}/schedules", json={'day_of_week': dow, 'start_time': st, 'end_time': en})
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/edit')
def edit_doctor(did):
    doc = api_get(f'/doctors/{did}')
    if doc is None:
        return redirect(url_for('doctors'))
    return render_template('doctors_edit.html', doctor=doc, action=url_for('update_doctor', did=did))


@app.route('/doctors/<int:did>', methods=['POST'])
def update_doctor(did):
    data = {k: request.form.get(k) for k in ('first_name', 'last_name', 'email', 'phone', 'speciality_id', 'registration_number')}
    api_send('PUT', f'/doctors/{did}', json=data, success='Doctor updated')
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/delete', methods=['POST'])
def delete_doctor(did):
    api_send('DELETE', f'/doctors/{did}', success='Doctor deleted')
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/schedules', methods=['POST'])
def add_schedule(did):
    dow = int(request.form.get('day_of_week'))
    start = request.form.get('start_time')
    end = request.form.get('end_time')
    api_send('POST', f'/doctors/{did}/schedules', json={'day_of_week': dow, 'start_time': start, 'end_time': end}, success='Schedule added')
    return redirect(url_for('edit_doctor', did=did))


@app.route('/schedules/<int:sid>/delete', methods=['POST'])
def delete_schedule(sid):
    api_send('DELETE', f'/schedules/{sid}', success='Schedule deleted')
    return redirect(request.referrer or url_for('doctors'))


# --- Appointments -----------------------------------------------------------
@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    data = {
        'doctor_id': int(request.form.get('doctor_id')),
        'patient_id': int(request.form.get('patient_id')),
        'appointment_date': request.form.get('appointment_date'),
        'start_time': request.form.get('start_time'),
        'slot_minutes': int(request.form.get('slot_minutes') or 10),
    }
    api_send('POST', '/appointments', json=data, success='Appointment booked')
    return redirect(url_for('appointments'))


@app.route('/appointments')
def appointments():
    appts = api_get('/appointments', default=[])
    u = session.get('user') or {}
    return render_template(
        'appointments.html',
        appointments=appts,
        stats={'total': len(appts)},
        current_role=u.get('role', ''),
        current_doctor_id=u.get('doctor_id') or '',
    )


@app.route('/appointments/<int:aid>/edit', methods=['GET'])
def edit_appointment(aid):
    appt = api_get(f'/appointments/{aid}')
    if appt is None:
        return redirect(url_for('appointments'))
    return render_template('appointments_edit.html', appointment=appt, action=url_for('update_appointment', aid=aid))


@app.route('/appointments/<int:aid>', methods=['POST'])
def update_appointment(aid):
    data = {
        'prescription': request.form.get('prescription', ''),
        'status': request.form.get('status', 'confirmed'),
    }
    api_send('PUT', f'/appointments/{aid}', json=data, success='Appointment updated')
    return redirect(url_for('appointments'))


@app.route('/reports')
def reports():
    return render_template('reports.html')


# --- Billing dashboard ------------------------------------------------------
@app.route('/billing/dashboard')
def billing_dashboard():
    period = request.args.get('period')
    year = request.args.get('year')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    params = {}
    if period:
        params['period'] = period
    if year:
        params['year'] = year
    if start_date and end_date:
        params['start_date'] = start_date
        params['end_date'] = end_date
    data = api_get('/reports/billing', params=params, default=None)
    report = months = None
    if data:
        report = data if (period or (start_date and end_date and 'by_month' in data)) else None
        months = data.get('by_month') if (year or (start_date and end_date)) else None
    return render_template('dashboard_billing.html', report=report, months=months)


# --- Transactions -----------------------------------------------------------
@app.route('/billing/transactions')
def billing_transactions():
    ttype = request.args.get('type')
    params = {'type': ttype} if ttype else None
    return render_template('transactions.html', transactions=api_get('/billing/transactions', params=params, default=[]))


@app.route('/billing/transactions/new')
def new_billing_transaction():
    return render_template('transactions_edit.html', transaction=None, action=url_for('create_billing_transaction_route'))


@app.route('/billing/transactions', methods=['POST'])
def create_billing_transaction_route():
    data = {'trans_date': request.form.get('trans_date'), 'amount': request.form.get('amount'), 'type': request.form.get('type'), 'description': request.form.get('description')}
    api_send('POST', '/billing/transactions', json=data, success='Transaction created')
    return redirect(url_for('billing_transactions'))


@app.route('/billing/transactions/<int:tid>/edit')
def edit_billing_transaction(tid):
    txs = api_get('/billing/transactions', default=[])
    tr = next((x for x in txs if x.get('id') == tid), None)
    if not tr:
        return redirect(url_for('billing_transactions'))
    return render_template('transactions_edit.html', transaction=tr, action=url_for('update_billing_transaction_route', tid=tid))


@app.route('/billing/transactions/<int:tid>', methods=['POST'])
def update_billing_transaction_route(tid):
    data = {'trans_date': request.form.get('trans_date'), 'amount': request.form.get('amount'), 'type': request.form.get('type'), 'description': request.form.get('description')}
    api_send('PUT', f'/billing/transactions/{tid}', json=data, success='Transaction updated')
    return redirect(url_for('billing_transactions'))


@app.route('/billing/transactions/<int:tid>/delete', methods=['POST'])
def delete_billing_transaction_route(tid):
    api_send('DELETE', f'/billing/transactions/{tid}', success='Transaction deleted')
    return redirect(url_for('billing_transactions'))


@app.route('/expenses')
def expenses():
    return render_template('transactions.html', transactions=api_get('/billing/transactions', params={'type': 'expense'}, default=[]))


# --- Invoices ---------------------------------------------------------------
@app.route('/invoices')
def invoices():
    return render_template('invoices.html', invoices=api_get('/invoices', default=[]))


@app.route('/invoices/new')
def new_invoice():
    return render_template('invoice_edit.html', invoice=None, action=url_for('create_invoice'))


@app.route('/invoices', methods=['POST'])
def create_invoice():
    invoice_date = request.form.get('invoice_date')
    patient_id = request.form.get('patient_id')
    descs = request.form.getlist('desc')
    qtys = request.form.getlist('qty')
    ups = request.form.getlist('unit_price')
    lines = []
    for i in range(len(descs)):
        if not descs[i]:
            continue
        lines.append({'description': descs[i], 'qty': int(qtys[i] or 1), 'unit_price': float(ups[i] or 0)})
    payload = {'invoice_date': invoice_date, 'patient_id': patient_id, 'lines': lines}
    api_send('POST', '/invoices', json=payload, success='Invoice created')
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>/edit')
def edit_invoice(iid):
    inv = api_get(f'/invoices/{iid}')
    if inv is None:
        return redirect(url_for('invoices'))
    return render_template('invoice_edit.html', invoice=inv, action=url_for('update_invoice', iid=iid))


@app.route('/invoices/<int:iid>', methods=['POST'])
def update_invoice(iid):
    payload = {'invoice_date': request.form.get('invoice_date'), 'patient_id': request.form.get('patient_id')}
    api_send('PUT', f'/invoices/{iid}', json=payload, success='Invoice updated')
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>/delete', methods=['POST'])
def delete_invoice(iid):
    api_send('DELETE', f'/invoices/{iid}', success='Invoice deleted')
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>')
def view_invoice(iid):
    inv = api_get(f'/invoices/{iid}')
    if inv is None:
        return redirect(url_for('invoices'))
    return render_template('invoice_view.html', invoice=inv)


@app.route('/invoices/<int:iid>/export')
def export_invoice(iid):
    try:
        r = requests.get(f'{API_URL}/invoices/{iid}/export', headers=api_headers(), timeout=30)
        if r.status_code == 200:
            resp = make_response(r.content)
            cd = r.headers.get('Content-Disposition') or f'attachment; filename=invoice_{iid}.pdf'
            resp.headers['Content-Disposition'] = cd
            resp.headers['Content-Type'] = r.headers.get('Content-Type', 'application/pdf')
            return resp
        flash(_api_error(r), 'danger')
    except requests.exceptions.RequestException:
        flash('Cannot reach the API server — is it running?', 'danger')
    return redirect(url_for('view_invoice', iid=iid))


@app.route('/invoices/<int:iid>/payments', methods=['POST'])
def create_invoice_payment(iid):
    payload = {
        'invoice_id': iid,
        'payment_date': request.form.get('payment_date') or None,
        'amount': request.form.get('amount'),
        'method': request.form.get('method'),
        'reference': request.form.get('reference'),
    }
    api_send('POST', '/payments', json=payload, success='Payment recorded')
    return redirect(url_for('view_invoice', iid=iid))


@app.route('/payments/<int:pid>/delete', methods=['POST'])
def delete_payment(pid):
    api_send('DELETE', f'/payments/{pid}', success='Payment deleted')
    return redirect(request.referrer or url_for('invoices'))


# --- Roles ------------------------------------------------------------------
@app.route('/roles')
def roles():
    return render_template('roles.html', roles=api_get('/roles', default=[]))


@app.route('/roles', methods=['POST'])
def create_role_route():
    data = {'name': request.form.get('name'), 'description': request.form.get('description')}
    api_send('POST', '/roles', json=data, success='Role created')
    return redirect(url_for('roles'))


@app.route('/roles/<rname>/delete', methods=['POST'])
def delete_role_route(rname):
    api_send('DELETE', f'/roles/{rname}', success='Role deleted')
    return redirect(url_for('roles'))


@app.route('/roles/<rname>', methods=['PUT'])
def update_role_route(rname):
    # AJAX endpoint: returns JSON for client-side JS (no flash).
    body = request.get_json(force=True, silent=True) or {}
    payload = {'name': body.get('name'), 'description': body.get('description')}
    try:
        r = requests.put(f'{API_URL}/roles/{rname}', json=payload, headers=api_headers(), timeout=API_TIMEOUT)
        if r.status_code == 200:
            return jsonify({'success': True})
        return jsonify({'error': _api_error(r)}), r.status_code
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Cannot reach the API server'}), 502


# --- Users ------------------------------------------------------------------
@app.route('/users')
def users():
    return render_template('users.html', users=api_get('/users', default=[]))


@app.route('/users/new')
def new_user():
    return render_template('users_edit.html', user=None, action=url_for('create_user'), roles=api_get('/roles', default=[]))


@app.route('/users/<int:uid>/edit')
def edit_user(uid):
    if uid == 0:
        return redirect(url_for('new_user'))
    u = api_get(f'/users/{uid}')
    if u is None:
        return redirect(url_for('users'))
    return render_template('users_edit.html', user=u, action=url_for('update_user', uid=uid), roles=api_get('/roles', default=[]))


def _user_form_data():
    return {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'is_admin': bool(request.form.get('is_admin')),
        'is_active': bool(request.form.get('is_active')),
        'role': request.form.get('role'),
        'doctor_id': int(request.form.get('doctor_id')) if request.form.get('doctor_id') else None,
    }


@app.route('/users', methods=['POST'])
def create_user():
    api_send('POST', '/users', json=_user_form_data(), success='User created successfully')
    return redirect(url_for('users'))


@app.route('/users/<int:uid>', methods=['POST'])
def update_user(uid):
    api_send('PUT', f'/users/{uid}', json=_user_form_data(), success='User updated successfully')
    return redirect(url_for('users'))


@app.route('/users/<int:uid>/delete', methods=['POST'])
def delete_user(uid):
    api_send('DELETE', f'/users/{uid}', success='User deleted')
    return redirect(url_for('users'))


# --- Admin: permission management -------------------------------------------
@app.route('/admin/permissions')
def admin_permissions():
    if not session.get('user') or not session.get('user').get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))

    screens = ['appointments', 'patients', 'doctors', 'specialities', 'invoices', 'transactions', 'dashboard', 'users', 'roles']
    actions = ['view', 'add', 'edit', 'delete']
    roles = api_get('/roles', default=[])
    screen_perms = api_get('/admin/screen-permissions', default=[])
    action_perms = api_get('/admin/action-permissions', default=[])

    def action_perm_exists(role, screen, action):
        return any(p['role_name'] == role and p['screen_name'] == screen and p['action'] == action for p in action_perms)

    return render_template('admin_permissions.html',
                           roles=roles,
                           screens=screens,
                           actions=actions,
                           screen_perms=screen_perms,
                           action_perms=action_perms,
                           action_perm_exists=action_perm_exists)


if __name__ == '__main__':
    host = os.getenv('WEB_HOST', '0.0.0.0')
    port = int(os.getenv('WEB_PORT', '3003'))
    app.run(host=host, port=port)
