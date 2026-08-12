"""Minimal Flask web frontend for iCare+ (serves templates and proxies simple API calls).
Uses `API_URL` environment variable (default http://localhost:8004).
"""
from flask import Flask, render_template, request
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
