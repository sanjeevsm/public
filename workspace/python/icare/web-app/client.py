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
