import os
import unittest
import requests

BASE = os.getenv('API_URL', 'http://localhost:5000')


# ── SPECIALITIES ──────────────────────────────────────────────────────────────

class TestSpecialities(unittest.TestCase):

    def test_list(self):
        r = requests.get(f'{BASE}/specialities')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)
        self.assertGreater(len(r.json()), 0)

    def test_get_one(self):
        r = requests.get(f'{BASE}/specialities/1')
        self.assertEqual(r.status_code, 200)
        self.assertIn('name', r.json())

    def test_not_found(self):
        r = requests.get(f'{BASE}/specialities/99999')
        self.assertEqual(r.status_code, 404)

    def test_create_update_delete(self):
        r = requests.post(f'{BASE}/specialities', json={'name': 'Test Speciality'})
        self.assertEqual(r.status_code, 201)
        sid = r.json()['id']

        r = requests.put(f'{BASE}/specialities/{sid}', json={'name': 'Updated Speciality'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['name'], 'Updated Speciality')

        r = requests.delete(f'{BASE}/specialities/{sid}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['deleted'], sid)

        r = requests.get(f'{BASE}/specialities/{sid}')
        self.assertEqual(r.status_code, 404)


# ── DOCTORS ───────────────────────────────────────────────────────────────────

class TestDoctors(unittest.TestCase):

    def test_list(self):
        r = requests.get(f'{BASE}/doctors')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json()), 0)

    def test_get_one(self):
        r = requests.get(f'{BASE}/doctors/1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('first_name', data)
        self.assertIn('speciality_name', data)

    def test_not_found(self):
        r = requests.get(f'{BASE}/doctors/99999')
        self.assertEqual(r.status_code, 404)

    def test_create_update_delete(self):
        payload = {
            'first_name': 'Test', 'last_name': 'Doctor',
            'email': 'test.doctor@clinic.test', 'phone': '0000000099',
            'registration_number': 'TST-TEST-999', 'speciality_id': 1,
            'bio': 'Test bio', 'consultation_fee': 500,
        }
        r = requests.post(f'{BASE}/doctors', json=payload)
        self.assertEqual(r.status_code, 201)
        did = r.json()['id']

        payload['first_name'] = 'Updated'
        r = requests.put(f'{BASE}/doctors/{did}', json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['first_name'], 'Updated')

        r = requests.delete(f'{BASE}/doctors/{did}')
        self.assertEqual(r.status_code, 200)

    def test_by_speciality(self):
        r = requests.get(f'{BASE}/doctors/by-speciality/1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for doc in data:
            self.assertEqual(doc['speciality_id'], 1)

    def test_by_slot(self):
        # Doctor 1 has Monday (1) schedule 09:00–13:00
        r = requests.get(f'{BASE}/doctors/by-slot?day_of_week=1&start_time=09:00')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)
        self.assertGreater(len(r.json()), 0)

    def test_by_slot_missing_params(self):
        r = requests.get(f'{BASE}/doctors/by-slot?day_of_week=1')
        self.assertEqual(r.status_code, 400)


# ── SCHEDULES ─────────────────────────────────────────────────────────────────

class TestSchedules(unittest.TestCase):

    def test_list(self):
        r = requests.get(f'{BASE}/schedules')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json()), 0)

    def test_get_one(self):
        r = requests.get(f'{BASE}/schedules/1')
        self.assertEqual(r.status_code, 200)
        self.assertIn('doctor_id', r.json())

    def test_not_found(self):
        r = requests.get(f'{BASE}/schedules/99999')
        self.assertEqual(r.status_code, 404)

    def test_create_update_delete(self):
        # Doctor 1 has no Saturday (6) schedule — safe to create
        payload = {
            'doctor_id': 1, 'day_of_week': 6,
            'start_time': '20:00', 'end_time': '22:00',
            'slot_duration_minutes': 30,
        }
        r = requests.post(f'{BASE}/schedules', json=payload)
        self.assertEqual(r.status_code, 201)
        sid = r.json()['id']

        payload['end_time'] = '22:30'
        r = requests.put(f'{BASE}/schedules/{sid}', json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['end_time'], '22:30:00')

        r = requests.delete(f'{BASE}/schedules/{sid}')
        self.assertEqual(r.status_code, 200)

    def test_by_doctor(self):
        r = requests.get(f'{BASE}/schedules/by-doctor/1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertGreater(len(data), 0)
        for s in data:
            self.assertEqual(s['doctor_id'], 1)

    def test_by_speciality(self):
        r = requests.get(f'{BASE}/schedules/by-speciality/1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for s in data:
            self.assertIn('speciality_name', s)


# ── PATIENTS ──────────────────────────────────────────────────────────────────

class TestPatients(unittest.TestCase):

    def test_list(self):
        r = requests.get(f'{BASE}/patients')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json()), 0)

    def test_get_one(self):
        r = requests.get(f'{BASE}/patients/1')
        self.assertEqual(r.status_code, 200)
        self.assertIn('first_name', r.json())

    def test_not_found(self):
        r = requests.get(f'{BASE}/patients/99999')
        self.assertEqual(r.status_code, 404)

    def test_create_update_delete(self):
        payload = {
            'first_name': 'Test', 'last_name': 'Patient',
            'phone': '8800000099', 'email': 'test.patient@test.com',
            'date_of_birth': '1990-01-01', 'gender': 'Male',
        }
        r = requests.post(f'{BASE}/patients', json=payload)
        self.assertEqual(r.status_code, 201)
        pid = r.json()['id']

        payload['first_name'] = 'Updated'
        r = requests.put(f'{BASE}/patients/{pid}', json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['first_name'], 'Updated')

        r = requests.delete(f'{BASE}/patients/{pid}')
        self.assertEqual(r.status_code, 200)

    def test_by_doctor(self):
        # Doctor 1 has completed appointments — should have patients
        r = requests.get(f'{BASE}/patients/by-doctor/1')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)
        self.assertGreater(len(r.json()), 0)


# ── APPOINTMENTS ──────────────────────────────────────────────────────────────

class TestAppointments(unittest.TestCase):

    def test_list(self):
        r = requests.get(f'{BASE}/appointments')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json()), 0)

    def test_get_one(self):
        r = requests.get(f'{BASE}/appointments/1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('doctor_name', data)
        self.assertIn('patient_name', data)

    def test_not_found(self):
        r = requests.get(f'{BASE}/appointments/99999')
        self.assertEqual(r.status_code, 404)

    def test_create_update_delete(self):
        # Doctor 7 (Suresh Patel) works Tue; 2026-06-02 is a Tuesday
        payload = {
            'doctor_id': 7, 'patient_id': 1,
            'appointment_date': '2026-06-02',
            'start_time': '08:45', 'end_time': '09:00',
            'status': 'confirmed',
        }
        r = requests.post(f'{BASE}/appointments', json=payload)
        self.assertEqual(r.status_code, 201)
        aid = r.json()['id']

        payload['status'] = 'cancelled'
        r = requests.put(f'{BASE}/appointments/{aid}', json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'cancelled')

        r = requests.delete(f'{BASE}/appointments/{aid}')
        self.assertEqual(r.status_code, 200)

    def test_by_doctor(self):
        r = requests.get(f'{BASE}/appointments/by-doctor/1')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertGreater(len(data), 0)
        for a in data:
            self.assertEqual(a['doctor_id'], 1)


# ── BOOK APPOINTMENT ──────────────────────────────────────────────────────────

class TestBookAppointment(unittest.TestCase):

    # Doctor 7 (Suresh Patel): Mon–Fri 08:00–12:00, 15-min slots
    # 2026-06-01 = Monday, 2026-06-08 = Monday (both clear of existing data)

    def test_book_success(self):
        payload = {
            'patient_id': 1, 'doctor_id': 7,
            'appointment_date': '2026-06-01',
            'start_time': '08:15', 'end_time': '08:30',
        }
        r = requests.post(f'{BASE}/appointments/book', json=payload)
        self.assertEqual(r.status_code, 201)
        data = r.json()
        self.assertEqual(data['doctor_id'], 7)
        self.assertEqual(data['patient_id'], 1)
        self.assertEqual(data['status'], 'confirmed')
        # cleanup
        requests.delete(f'{BASE}/appointments/{data["id"]}')

    def test_book_duplicate_slot(self):
        payload = {
            'patient_id': 2, 'doctor_id': 7,
            'appointment_date': '2026-06-08',
            'start_time': '09:00', 'end_time': '09:15',
        }
        r1 = requests.post(f'{BASE}/appointments/book', json=payload)
        self.assertEqual(r1.status_code, 201)

        r2 = requests.post(f'{BASE}/appointments/book', json=payload)
        self.assertEqual(r2.status_code, 409)
        self.assertIn('error', r2.json())

        requests.delete(f'{BASE}/appointments/{r1.json()["id"]}')

    def test_book_invalid_slot(self):
        # Doctor 1 has no Sunday schedule; 2026-06-07 = Sunday
        payload = {
            'patient_id': 1, 'doctor_id': 1,
            'appointment_date': '2026-06-07',
            'start_time': '09:00', 'end_time': '09:30',
        }
        r = requests.post(f'{BASE}/appointments/book', json=payload)
        self.assertEqual(r.status_code, 422)

    def test_book_patient_not_found(self):
        payload = {
            'patient_id': 99999, 'doctor_id': 7,
            'appointment_date': '2026-06-01',
            'start_time': '10:00', 'end_time': '10:15',
        }
        r = requests.post(f'{BASE}/appointments/book', json=payload)
        self.assertEqual(r.status_code, 404)

    def test_book_missing_fields(self):
        r = requests.post(f'{BASE}/appointments/book', json={'patient_id': 1, 'doctor_id': 7})
        self.assertEqual(r.status_code, 400)


# ── CASE HISTORY ──────────────────────────────────────────────────────────────

class TestCaseHistory(unittest.TestCase):

    def test_list(self):
        r = requests.get(f'{BASE}/case-history')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json()), 0)

    def test_get_one(self):
        r = requests.get(f'{BASE}/case-history/1')
        self.assertEqual(r.status_code, 200)
        self.assertIn('appointment_id', r.json())

    def test_not_found(self):
        r = requests.get(f'{BASE}/case-history/99999')
        self.assertEqual(r.status_code, 404)

    def test_create_update_delete(self):
        # Create a throwaway appointment (bypass book validation)
        appt = requests.post(f'{BASE}/appointments', json={
            'doctor_id': 9, 'patient_id': 3,
            'appointment_date': '2026-06-03',   # Tuesday, Doctor 9 works Tue
            'start_time': '11:30', 'end_time': '11:45',
            'status': 'completed',
        }).json()
        aid = appt['id']

        r = requests.post(f'{BASE}/case-history', json={
            'appointment_id': aid,
            'symptoms': 'Headache', 'diagnosis': 'Migraine',
            'prescription': 'Rest', 'follow_up_needed': False,
            'notes': 'Monitor',
        })
        self.assertEqual(r.status_code, 201)
        chid = r.json()['id']

        r = requests.put(f'{BASE}/case-history/{chid}', json={
            'symptoms': 'Severe headache', 'diagnosis': 'Chronic migraine',
            'prescription': 'Topiramate', 'follow_up_needed': True,
            'follow_up_date': '2026-07-01', 'notes': 'Follow up in 6 weeks',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['diagnosis'], 'Chronic migraine')

        requests.delete(f'{BASE}/case-history/{chid}')
        requests.delete(f'{BASE}/appointments/{aid}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
