# test_api_data.py
"""
This API Endpoint test will ensure that the API endpoints /requirement1 and /requirement2 return the expected data when queried.
""" 
import unittest
from ..app import app

class TestApiData(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_requirement1_endpoint(self):
        response = self.app.get('/requirement1')

        self.assertEqual(response.status_code, 200)
        # Checking the response content for expected data
        self.assertIn('Expected Data', response.data.decode())
    
    def test_requirement2_endpoint(self):
        response = self.app.get('/requirement2')

        self.assertEqual(response.status_code, 200)
        # Checking the response content for expected data
        self.assertIn('Expected Data', response.data.decode())

if __name__ == '__main__':
    unittest.main()
