"""Minimal Flask web frontend for iCare+ (serves templates and proxies simple API calls).
Uses `API_URL` environment variable (default http://localhost:8004).
"""
from flask import Flask, render_template, request, redirect, url_for
import os
import requests

app = Flask(__name__, template_folder='.')
API_URL = os.getenv('API_URL', 'http://localhost:8004')


@app.context_processor
def inject_api_url():
    return dict(api_url=API_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/specialities')
def specialities():
    r = requests.get(f'{API_URL}/specialities', timeout=5)
    return render_template('specialities.html', specialities=r.json())


@app.route('/specialities/new')
def new_speciality():
    return render_template('specialities_edit.html', speciality=None, action=url_for('create_speciality'))


@app.route('/specialities', methods=['POST'])
def create_speciality():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('specialities'))
    try:
        requests.post(f'{API_URL}/specialities', json={'name': name}, timeout=5)
    except Exception:
        pass
    return redirect(url_for('specialities'))


@app.route('/specialities/<int:sid>/edit')
def edit_speciality(sid):
    r = requests.get(f'{API_URL}/specialities/{sid}', timeout=5)
    if r.status_code != 200:
        return redirect(url_for('specialities'))
    return render_template('specialities_edit.html', speciality=r.json(), action=url_for('update_speciality', sid=sid))


@app.route('/specialities/<int:sid>', methods=['POST'])
def update_speciality(sid):
    name = request.form.get('name')
    if name:
        try:
            requests.put(f'{API_URL}/specialities/{sid}', json={'name': name}, timeout=5)
        except Exception:
            pass
    return redirect(url_for('specialities'))


@app.route('/specialities/<int:sid>/delete', methods=['POST'])
def delete_speciality(sid):
    try:
        requests.delete(f'{API_URL}/specialities/{sid}', timeout=5)
    except Exception:
        pass
    return redirect(url_for('specialities'))


@app.route('/patients')
def patients():
    r = requests.get(f'{API_URL}/patients', timeout=5)
    return render_template('patients.html', patients=r.json())


@app.route('/doctors')
def doctors():
    r = requests.get(f'{API_URL}/doctors', timeout=5)
    return render_template('doctors.html', doctors=r.json())


@app.route('/doctors/new')
def new_doctor():
    return render_template('doctors_edit.html', doctor=None, action=url_for('create_doctor'))


@app.route('/doctors', methods=['POST'])
def create_doctor():
    data = {k: request.form.get(k) for k in ('first_name','last_name','email','phone','speciality_id')}
    try:
        requests.post(f'{API_URL}/doctors', json=data, timeout=5)
    except Exception:
        pass
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/edit')
def edit_doctor(did):
    r = requests.get(f'{API_URL}/doctors/{did}', timeout=5)
    if r.status_code != 200:
        return redirect(url_for('doctors'))
    return render_template('doctors_edit.html', doctor=r.json(), action=url_for('update_doctor', did=did))


@app.route('/doctors/<int:did>', methods=['POST'])
def update_doctor(did):
    data = {k: request.form.get(k) for k in ('first_name','last_name','email','phone','speciality_id')}
    try:
        requests.put(f'{API_URL}/doctors/{did}', json=data, timeout=5)
    except Exception:
        pass
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/delete', methods=['POST'])
def delete_doctor(did):
    try:
        requests.delete(f'{API_URL}/doctors/{did}', timeout=5)
    except Exception:
        pass
    return redirect(url_for('doctors'))


@app.route('/doctors/<int:did>/schedules', methods=['POST'])
def add_schedule(did):
    dow = int(request.form.get('day_of_week'))
    start = request.form.get('start_time')
    end = request.form.get('end_time')
    try:
        requests.post(f'{API_URL}/doctors/{did}/schedules', json={'day_of_week': dow, 'start_time': start, 'end_time': end}, timeout=5)
    except Exception:
        pass
    return redirect(url_for('edit_doctor', did=did))


@app.route('/schedules/<int:sid>/delete', methods=['POST'])
def delete_schedule(sid):
    try:
        requests.delete(f'{API_URL}/schedules/{sid}', timeout=5)
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
        r = requests.post(f'{API_URL}/appointments', json=data, timeout=5)
        if r.status_code != 201:
            # ignore for now
            pass
    except Exception:
        pass
    return redirect(url_for('appointments'))


@app.route('/appointments')
def appointments():
    r = requests.get(f'{API_URL}/appointments', timeout=5)
    return render_template('appointments.html', appointments=r.json(), stats={'total': len(r.json())})


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', '3003'))
    app.run(host='0.0.0.0', port=port)
