# test_api_endpoint.py
"""
This Integration test will ensure that the API endpoint /upload correctly handles file uploads and data migration. 
""" 
import unittest
from ..app import app
import io

class TestApiEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_upload_csv_endpoint(self):
        # Testing data
        test_file = (io.BytesIO(b'1,Angel Lavado,2021-11-07T02:48:42Z,2,95'), 'hired_employees_test.csv')
        table_name = 'hired_employees.csv'

        response = self.app.post('/upload', data={'table_name': table_name}, files={'file': test_file})

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
