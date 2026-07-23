import os
from collections import Counter
from datetime import datetime
import requests as http
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)

API  = os.getenv('API_URL', 'http://localhost:5000')
DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

POKEMON = [
    (6,   'Charizard'),
    (113, 'Chansey'),
    (68,  'Machamp'),
    (35,  'Clefairy'),
    (65,  'Alakazam'),
    (134, 'Vaporeon'),
    (143, 'Snorlax'),
    (12,  'Butterfree'),
    (94,  'Gengar'),
    (78,  'Rapidash'),
]

ARTWORK = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png'
SPRITE  = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png'

BADGE_COLORS = [
    ('#fef3c7', '#b45309'),
    ('#dbeafe', '#1d4ed8'),
    ('#dcfce7', '#15803d'),
    ('#fce7f3', '#be185d'),
    ('#ede9fe', '#6d28d9'),
    ('#ffedd5', '#c2410c'),
    ('#cffafe', '#0e7490'),
    ('#f0fdf4', '#166534'),
]


def fetch(path):
    try:
        resp = http.get(f'{API}{path}', timeout=10)
        data = resp.json()
        if isinstance(data, dict) and 'error' in data:
            print(f'[API ERROR] GET {path} -> {data["error"]}', flush=True)
            return []
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f'[FETCH ERROR] GET {path} -> {e}', flush=True)
        return []


def enrich_doctors(doctors):
    schedules = fetch('/schedules')
    sched_map = {}
    for s in schedules:
        sched_map.setdefault(s['doctor_id'], set()).add(s['day_of_week'])

    specialities = sorted({d['speciality_name'] for d in doctors})
    color_map    = {
        spec: BADGE_COLORS[i % len(BADGE_COLORS)]
        for i, spec in enumerate(specialities)
    }

    for i, d in enumerate(doctors):
        pid, pname    = POKEMON[i % len(POKEMON)]
        d['artwork']  = ARTWORK.format(pid)
        d['sprite']   = SPRITE.format(pid)
        d['pokemon']  = pname
        days          = sorted(sched_map.get(d['id'], []))
        d['days']     = ', '.join(DAYS[x] for x in days) or '—'
        bg, fg        = color_map[d['speciality_name']]
        d['badge_bg'] = bg
        d['badge_fg'] = fg
    return doctors


@app.route('/')
def index():
    doctors     = enrich_doctors(fetch('/doctors'))
    spec_counts = Counter(d['speciality_name'] for d in doctors)
    # Only specialities that have at least one doctor
    specialities = [{'name': s, 'count': spec_counts[s]} for s in sorted(spec_counts)]
    return render_template('index.html', doctors=doctors, specialities=specialities)


@app.route('/appointments')
def appointments():
    data  = fetch('/appointments')
    stats = {
        'total':     len(data),
        'confirmed': sum(1 for a in data if a['status'] == 'confirmed'),
        'completed': sum(1 for a in data if a['status'] == 'completed'),
        'cancelled': sum(1 for a in data if a['status'] == 'cancelled'),
    }
    return render_template('appointments.html', appointments=data, stats=stats)


@app.route('/patients')
def patients():
    return render_template('patients.html', patients=fetch('/patients'))


@app.route('/specialities')
def specialities():
    return render_template('specialities.html', specialities=fetch('/specialities'))


@app.route('/schedules')
def schedules():
    all_sched = fetch('/schedules')
    doc_map   = {d['id']: f"Dr. {d['first_name']} {d['last_name']}"
                 for d in fetch('/doctors')}
    for s in all_sched:
        s['doctor_name'] = doc_map.get(s['doctor_id'], f"Doctor #{s['doctor_id']}")
        s['day_name']    = DAYS[s['day_of_week']]
        s['time_range']  = f"{s['start_time'][:5]} – {s['end_time'][:5]}"
    return render_template('schedules.html', schedules=all_sched)


@app.route('/leaves')
def leaves():
    all_leaves = fetch('/leaves')
    doctors    = fetch('/doctors')
    for lv in all_leaves:
        date_str = lv.get('leave_date', '')
        if date_str:
            try:
                parsed = datetime.strptime(date_str[:10], '%Y-%m-%d')
                lv['day_name'] = parsed.strftime('%A')
            except Exception:
                lv['day_name'] = ''
        else:
            lv['day_name'] = ''
    return render_template('leaves.html', leaves=all_leaves, doctors=doctors)


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', '5001'))
    app.run(debug=True, port=port)
