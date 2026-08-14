"""Minimal Flask web frontend for iCare+ (serves templates and proxies simple API calls).
Uses `API_URL` environment variable (default http://localhost:8004).
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
from flask import session, flash, Response, make_response
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from functools import wraps

app = Flask(__name__, template_folder='.')
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = os.getenv('WEB_SECRET', 'dev-secret')
API_URL = os.getenv('API_URL', 'http://localhost:8004')


def api_headers():
    h = {}
    if session.get('token'):
        h['Authorization'] = f"Bearer {session.get('token')}"
    return h


@app.context_processor
def inject_api_url():
    return dict(api_url=API_URL)


@app.route('/')
def index():
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
        r = requests.post(f'{API_URL}/auth/login', json={'username': username, 'password': password}, timeout=5)
        if r.status_code == 200:
            payload = r.json()
            # API returns { user: {...}, token: '...' }
            session['user'] = payload.get('user') or payload
            session['token'] = payload.get('token')
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed', 'danger')
    except Exception:
        flash('Login error', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out', 'info')
    return redirect(url_for('index'))


@app.route('/specialities')
def specialities():
    r = requests.get(f'{API_URL}/specialities', headers=api_headers(), timeout=5)
    return render_template('specialities.html', specialities=r.json() if r.status_code==200 else [])


@app.route('/specialities/new')
def new_speciality():
    return render_template('specialities_edit.html', speciality=None, action=url_for('create_speciality'))


@app.route('/specialities', methods=['POST'])
def create_speciality():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('specialities'))
    try:
        requests.post(f'{API_URL}/specialities', json={'name': name}, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('specialities'))


@app.route('/specialities/<int:sid>/edit')
def edit_speciality(sid):
    r = requests.get(f'{API_URL}/specialities/{sid}', headers=api_headers(), timeout=5)
    if r.status_code != 200:
        return redirect(url_for('specialities'))
    return render_template('specialities_edit.html', speciality=r.json(), action=url_for('update_speciality', sid=sid))


@app.route('/specialities/<int:sid>', methods=['POST'])
def update_speciality(sid):
    name = request.form.get('name')
    if name:
        try:
            requests.put(f'{API_URL}/specialities/{sid}', json={'name': name}, headers=api_headers(), timeout=5)
        except Exception:
            pass
    return redirect(url_for('specialities'))


@app.route('/specialities/<int:sid>/delete', methods=['POST'])
def delete_speciality(sid):
    try:
        requests.delete(f'{API_URL}/specialities/{sid}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('specialities'))


@app.route('/patients')
def patients():
    r = requests.get(f'{API_URL}/patients', headers=api_headers(), timeout=5)
    return render_template('patients.html', patients=r.json() if r.status_code==200 else [])


@app.route('/patients/new')
def new_patient():
    return render_template('patients_edit.html', patient=None, action=url_for('create_patient'))


@app.route('/patients', methods=['POST'])
def create_patient():
    data = {k: request.form.get(k) for k in ('first_name','last_name','email','phone')}
    try:
        requests.post(f'{API_URL}/patients', json=data, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('patients'))


@app.route('/patients/<int:pid>/edit')
def edit_patient(pid):
    r = requests.get(f'{API_URL}/patients/{pid}', headers=api_headers(), timeout=5)
    if r.status_code != 200:
        return redirect(url_for('patients'))
    return render_template('patients_edit.html', patient=r.json(), action=url_for('update_patient', pid=pid))


@app.route('/patients/<int:pid>', methods=['POST'])
def update_patient(pid):
    data = {k: request.form.get(k) for k in ('first_name','last_name','email','phone')}
    try:
        requests.put(f'{API_URL}/patients/{pid}', json=data, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('patients'))


@app.route('/patients/<int:pid>/delete', methods=['POST'])
def delete_patient(pid):
    try:
        requests.delete(f'{API_URL}/patients/{pid}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('patients'))


@app.route('/schedules')
def schedules():
    return render_template('schedules.html')


@app.route('/leaves')
def leaves():
    return render_template('leaves.html')


@app.route('/leaves/new', methods=['POST'])
def create_leave_route():
    data = { 'doctor_id': int(request.form.get('doctor_id')), 'leave_date': request.form.get('leave_date'), 'reason': request.form.get('reason') }
    try:
        requests.post(f'{API_URL}/leaves', json=data, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('leaves'))


@app.route('/leaves/<int:lid>/delete', methods=['POST'])
def delete_leave_route(lid):
    try:
        requests.delete(f'{API_URL}/leaves/{lid}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('leaves'))


@app.route('/case_history')
def case_history():
    return render_template('case_history.html')


@app.route('/case_histories/new', methods=['POST'])
def create_case_history_route():
    data = { 'patient_id': int(request.form.get('patient_id')), 'notes': request.form.get('notes') }
    try:
        requests.post(f'{API_URL}/case_histories', json=data, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('case_history'))


@app.route('/case_histories/<int:cid>/delete', methods=['POST'])
def delete_case_history_route(cid):
    try:
        requests.delete(f'{API_URL}/case_histories/{cid}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('case_history'))





@app.route('/doctors')
def doctors():
    try:
        r = requests.get(f'{API_URL}/doctors', headers=api_headers(), timeout=5)
        s = requests.get(f'{API_URL}/specialities', headers=api_headers(), timeout=5)
        spec_map = {}
        if s.status_code == 200:
            for item in s.json():
                spec_map[item.get('id')] = item.get('name')
        return render_template('doctors.html', doctors=r.json() if r.status_code==200 else [], specialities=spec_map)
    except Exception:
        return render_template('doctors.html', doctors=[], specialities={})


@app.route('/doctors/new')
def new_doctor():
    return render_template('doctors_edit.html', doctor=None, action=url_for('create_doctor'))


@app.route('/doctors', methods=['POST'])
def create_doctor():
    # create doctor then optional schedules
    data = {k: request.form.get(k) for k in ('first_name','last_name','email','phone','speciality_id','registration_number')}
    try:
        r = requests.post(f'{API_URL}/doctors', json=data, headers=api_headers(), timeout=5)
        if r.status_code == 201:
            doc = r.json()
            # collect schedules from form arrays
            days = request.form.getlist('schedule_day[]') if 'schedule_day[]' in request.form else request.form.getlist('schedule_day')
            starts = request.form.getlist('schedule_start[]') if 'schedule_start[]' in request.form else request.form.getlist('schedule_start')
            ends = request.form.getlist('schedule_end[]') if 'schedule_end[]' in request.form else request.form.getlist('schedule_end')
            for i in range(len(days)):
                try:
                    dow = int(days[i])
                except Exception:
                    continue
                st = starts[i] if i < len(starts) else ''
                en = ends[i] if i < len(ends) else ''
                if st and en:
                    # ensure seconds
                    if len(st.split(':'))==2: st = st + ':00'
                    if len(en.split(':'))==2: en = en + ':00'
                    try:
                        requests.post(f"{API_URL}/doctors/{doc['id']}/schedules", json={'day_of_week': dow, 'start_time': st, 'end_time': en}, headers=api_headers(), timeout=5)
                    except Exception:
                        pass
    except Exception:
        pass
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/edit')
def edit_doctor(did):
    r = requests.get(f'{API_URL}/doctors/{did}', headers=api_headers(), timeout=5)
    if r.status_code != 200:
        return redirect(url_for('doctors'))
    return render_template('doctors_edit.html', doctor=r.json(), action=url_for('update_doctor', did=did))


@app.route('/doctors/<int:did>', methods=['POST'])
def update_doctor(did):
    data = {k: request.form.get(k) for k in ('first_name','last_name','email','phone','speciality_id','registration_number')}
    try:
        requests.put(f'{API_URL}/doctors/{did}', json=data, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/delete', methods=['POST'])
def delete_doctor(did):
    try:
        requests.delete(f'{API_URL}/doctors/{did}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/schedules', methods=['POST'])
def add_schedule(did):
    dow = int(request.form.get('day_of_week'))
    start = request.form.get('start_time')
    end = request.form.get('end_time')
    try:
        requests.post(f'{API_URL}/doctors/{did}/schedules', json={'day_of_week': dow, 'start_time': start, 'end_time': end}, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('edit_doctor', did=did))


@app.route('/schedules/<int:sid>/delete', methods=['POST'])
def delete_schedule(sid):
    try:
        requests.delete(f'{API_URL}/schedules/{sid}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    # redirect back to referer if present
    return redirect(request.referrer or url_for('doctors'))


@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    data = {
        'doctor_id': int(request.form.get('doctor_id')),
        'patient_id': int(request.form.get('patient_id')),
        'appointment_date': request.form.get('appointment_date'),
        'start_time': request.form.get('start_time'),
        'slot_minutes': int(request.form.get('slot_minutes') or 10)
    }
    try:
        r = requests.post(f'{API_URL}/appointments', json=data, headers=api_headers(), timeout=5)
        if r.status_code != 201:
            # ignore for now
            pass
    except Exception:
        pass
    return redirect(url_for('appointments'))


@app.route('/appointments')
def appointments():
    r = requests.get(f'{API_URL}/appointments', headers=api_headers(), timeout=5)
    appts = r.json() if r.status_code==200 else []
    return render_template('appointments.html', appointments=appts, stats={'total': len(appts)})


@app.route('/reports')
def reports():
    return render_template('reports.html')


# Billing dashboard proxy
@app.route('/billing/dashboard')
def billing_dashboard():
    period = request.args.get('period')
    year = request.args.get('year')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    headers = api_headers()
    params = {}
    if period:
        params['period'] = period
    if year:
        params['year'] = year
    if start_date and end_date:
        params['start_date'] = start_date
        params['end_date'] = end_date
    try:
        r = requests.get(f'{API_URL}/reports/billing', params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            report = data if period else None
            months = data.get('by_month') if year else None
            # For date range, get the summary from data
            if start_date and end_date and 'by_month' in data:
                report = data
                months = data.get('by_month')
            return render_template('dashboard_billing.html', report=report, months=months)
    except Exception:
        pass
    return render_template('dashboard_billing.html', report=None, months=None)


# Transactions UI
@app.route('/billing/transactions')
def billing_transactions():
    ttype = request.args.get('type')
    params = {}
    if ttype:
        params['type'] = ttype
    try:
        r = requests.get(f'{API_URL}/billing/transactions', params=params, headers=api_headers(), timeout=10)
        tx = r.json() if r.status_code==200 else []
    except Exception:
        tx = []
    return render_template('transactions.html', transactions=tx)


@app.route('/billing/transactions/new')
def new_billing_transaction():
    return render_template('transactions_edit.html', transaction=None, action=url_for('create_billing_transaction'))


@app.route('/billing/transactions', methods=['POST'])
def create_billing_transaction_route():
    data = {'trans_date': request.form.get('trans_date'), 'amount': request.form.get('amount'), 'type': request.form.get('type'), 'description': request.form.get('description')}
    try:
        requests.post(f'{API_URL}/billing/transactions', json=data, headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('billing_transactions'))


@app.route('/billing/transactions/<int:tid>/edit')
def edit_billing_transaction(tid):
    try:
        r = requests.get(f'{API_URL}/billing/transactions', headers=api_headers(), timeout=10)
        txs = r.json() if r.status_code==200 else []
        tr = next((x for x in txs if x.get('id')==tid), None)
    except Exception:
        tr = None
    if not tr:
        return redirect(url_for('billing_transactions'))
    return render_template('transactions_edit.html', transaction=tr, action=url_for('update_billing_transaction', tid=tid))


@app.route('/billing/transactions/<int:tid>', methods=['POST'])
def update_billing_transaction_route(tid):
    data = {'trans_date': request.form.get('trans_date'), 'amount': request.form.get('amount'), 'type': request.form.get('type'), 'description': request.form.get('description')}
    try:
        requests.put(f'{API_URL}/billing/transactions/{tid}', json=data, headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('billing_transactions'))


@app.route('/billing/transactions/<int:tid>/delete', methods=['POST'])
def delete_billing_transaction_route(tid):
    try:
        requests.delete(f'{API_URL}/billing/transactions/{tid}', headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('billing_transactions'))


@app.route('/expenses')
def expenses():
    # reuse transactions view filtered to expenses
    try:
        r = requests.get(f'{API_URL}/billing/transactions', params={'type':'expense'}, headers=api_headers(), timeout=10)
        tx = r.json() if r.status_code==200 else []
    except Exception:
        tx = []
    return render_template('transactions.html', transactions=tx)


# Invoices UI
@app.route('/invoices')
def invoices():
    try:
        r = requests.get(f'{API_URL}/invoices', headers=api_headers(), timeout=10)
        invs = r.json() if r.status_code==200 else []
    except Exception:
        invs = []
    return render_template('invoices.html', invoices=invs)


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
    try:
        requests.post(f'{API_URL}/invoices', json=payload, headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>/edit')
def edit_invoice(iid):
    try:
        r = requests.get(f'{API_URL}/invoices/{iid}', headers=api_headers(), timeout=10)
        if r.status_code==200:
            return render_template('invoice_edit.html', invoice=r.json(), action=url_for('update_invoice', iid=iid))
    except Exception:
        pass
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>', methods=['POST'])
def update_invoice(iid):
    invoice_date = request.form.get('invoice_date')
    patient_id = request.form.get('patient_id')
    descs = request.form.getlist('desc')
    qtys = request.form.getlist('qty')
    ups = request.form.getlist('unit_price')
    # For simplicity, delete existing lines then recreate via API endpoints would be better; here we will not modify lines on edit (basic support)
    payload = {'invoice_date': invoice_date, 'patient_id': patient_id}
    try:
        requests.put(f'{API_URL}/invoices/{iid}', json=payload, headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>/delete', methods=['POST'])
def delete_invoice(iid):
    try:
        requests.delete(f'{API_URL}/invoices/{iid}', headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>')
def view_invoice(iid):
    try:
        r = requests.get(f'{API_URL}/invoices/{iid}', headers=api_headers(), timeout=10)
        if r.status_code==200:
            inv = r.json()
            return render_template('invoice_view.html', invoice=inv)
    except Exception:
        pass
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:iid>/export')
def export_invoice(iid):
    try:
        r = requests.get(f'{API_URL}/invoices/{iid}/export', headers=api_headers(), timeout=30)
        if r.status_code == 200:
            resp = make_response(r.content)
            # forward content-disposition if provided
            cd = r.headers.get('Content-Disposition') or f'attachment; filename=invoice_{iid}.pdf'
            resp.headers['Content-Disposition'] = cd
            resp.headers['Content-Type'] = r.headers.get('Content-Type','application/pdf')
            return resp
    except Exception:
        pass
    return redirect(url_for('view_invoice', iid=iid))


@app.route('/invoices/<int:iid>/payments', methods=['POST'])
def create_invoice_payment(iid):
    payment_date = request.form.get('payment_date') or None
    amount = request.form.get('amount')
    method = request.form.get('method')
    reference = request.form.get('reference')
    payload = {'invoice_id': iid, 'payment_date': payment_date, 'amount': amount, 'method': method, 'reference': reference}
    try:
        requests.post(f'{API_URL}/payments', json=payload, headers=api_headers(), timeout=10)
    except Exception:
        pass
    return redirect(url_for('view_invoice', iid=iid))


@app.route('/payments/<int:pid>/delete', methods=['POST'])
def delete_payment(pid):
    try:
        requests.delete(f'{API_URL}/payments/{pid}', headers=api_headers(), timeout=10)
    except Exception:
        pass
    # cannot easily know invoice id here; redirect back
    return redirect(request.referrer or url_for('invoices'))


# Roles admin UI
@app.route('/roles')
def roles():
    # Admin can configure permissions in UI; menu shows all items to authenticated users
    try:
        r = requests.get(f'{API_URL}/roles', headers=api_headers(), timeout=5)
        roles_list = r.json() if r.status_code == 200 else []
    except Exception:
        roles_list = []
    return render_template('roles.html', roles=roles_list)


@app.route('/roles', methods=['POST'])
def create_role_route():
    name = request.form.get('name')
    description = request.form.get('description')
    try:
        requests.post(f'{API_URL}/roles', json={'name': name, 'description': description}, headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('roles'))


@app.route('/roles/<rname>/delete', methods=['POST'])
def delete_role_route(rname):
    try:
        requests.delete(f'{API_URL}/roles/{rname}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('roles'))


@app.route('/roles/<rname>', methods=['PUT'])
def update_role_route(rname):
    body = request.get_json(force=True, silent=True) or {}
    new_name = body.get('name')
    description = body.get('description')
    try:
        r = requests.put(f'{API_URL}/roles/{rname}', json={'name': new_name, 'description': description}, headers=api_headers(), timeout=5)
        if r.status_code == 200:
            return jsonify({'success': True})
        else:
            return jsonify({'error': r.json().get('error', 'Unknown error')}), r.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- User management routes -------------------------------------------------
@app.route('/users')
def users():
    try:
        r = requests.get(f'{API_URL}/users', headers=api_headers(), timeout=5)
        if r.status_code == 200:
            return render_template('users.html', users=r.json())
    except Exception:
        pass
    return render_template('users.html', users=[])


@app.route('/users/new')
def new_user():
    # fetch roles for select
    roles = []
    try:
        r = requests.get(f'{API_URL}/roles', headers=api_headers(), timeout=5)
        if r.status_code == 200:
            roles = r.json()
    except Exception:
        pass
    return render_template('users_edit.html', user=None, action=url_for('create_user'), roles=roles)


@app.route('/users/<int:uid>/edit')
def edit_user(uid):
    if uid == 0:
        return redirect(url_for('new_user'))
    try:
        r = requests.get(f'{API_URL}/users/{uid}', headers=api_headers(), timeout=5)
        roles = []
        rr = requests.get(f'{API_URL}/roles', headers=api_headers(), timeout=5)
        if rr.status_code == 200:
            roles = rr.json()
        if r.status_code == 200:
            return render_template('users_edit.html', user=r.json(), action=url_for('update_user', uid=uid), roles=roles)
    except Exception:
        pass
    return redirect(url_for('users'))


@app.route('/users', methods=['POST'])
def create_user():
    data = {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'is_admin': True if request.form.get('is_admin') else False,
        'is_active': True if request.form.get('is_active') else False,
        'role': request.form.get('role')
    }
    try:
        r = requests.post(f'{API_URL}/users', json=data, headers=api_headers(), timeout=5)
        if r.status_code == 201:
            flash('User created successfully', 'success')
        else:
            flash('Failed to create user', 'danger')
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'danger')
    return redirect(url_for('users'))


@app.route('/users/<int:uid>', methods=['POST'])
def update_user(uid):
    data = {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'is_admin': True if request.form.get('is_admin') else False,
        'is_active': True if request.form.get('is_active') else False,
        'role': request.form.get('role')
    }
    try:
        r = requests.put(f'{API_URL}/users/{uid}', json=data, headers=api_headers(), timeout=5)
        if r.status_code == 200:
            flash('User updated successfully', 'success')
        else:
            flash('Failed to update user', 'danger')
    except Exception as e:
        flash(f'Error updating user: {str(e)}', 'danger')
    return redirect(url_for('users'))


@app.route('/users/<int:uid>/delete', methods=['POST'])
def delete_user(uid):
    try:
        requests.delete(f'{API_URL}/users/{uid}', headers=api_headers(), timeout=5)
    except Exception:
        pass
    return redirect(url_for('users'))


@app.route('/admin/permissions')
def admin_permissions():
    """Admin page to manage screen-role and action permissions"""
    if not session.get('user') or not session.get('user').get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('index'))
    
    # Fetch all roles and permissions
    roles = []
    screen_perms = []
    action_perms = []
    screens = ['appointments', 'patients', 'doctors', 'specialities', 'invoices', 'transactions', 'dashboard', 'users', 'roles']
    actions = ['view', 'add', 'edit', 'delete']
    
    try:
        r = requests.get(f'{API_URL}/roles', headers=api_headers(), timeout=5)
        if r.status_code == 200:
            roles = r.json()
    except Exception:
        pass
    
    try:
        r = requests.get(f'{API_URL}/admin/screen-permissions', headers=api_headers(), timeout=5)
        if r.status_code == 200:
            screen_perms = r.json()
    except Exception:
        pass
    
    try:
        r = requests.get(f'{API_URL}/admin/action-permissions', headers=api_headers(), timeout=5)
        if r.status_code == 200:
            action_perms = r.json()
    except Exception:
        pass
    
    # Build helper for template
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
    port = int(os.getenv('WEB_PORT', '3003'))
    app.run(host='0.0.0.0', port=port)
