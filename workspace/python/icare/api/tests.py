import os
import unittest
import requests

BASE = os.getenv('API_URL', 'http://localhost:8004')


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
