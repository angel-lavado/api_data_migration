import unittest
from tests.test_api_data import TestApiData
from tests.test_upload_csv_to_sql import TestUploadCsvToSql
from tests.test_api_endpoint import TestApiEndpoint

if __name__ == '__main__':
    # Creating a test suite that includes all your test cases
    test_suite = unittest.TestSuite()

    # Adding test cases from different test files to the suite
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestApiData))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestUploadCsvToSql))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestApiEndpoint))

    # Running the test suite
    unittest.TextTestRunner(verbosity=2).run(test_suite)
