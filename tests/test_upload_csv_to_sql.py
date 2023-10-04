# test_upload_csv_to_sql.py
"""
This Unit test will ensure that the upload_csv_to_sql function correctly uploads CSV data to the Cloud SQL database. 
""" 
import unittest
import psycopg2
from ..app import upload_csv_to_sql
from ..config import TABLE_CONFIGS,DB_USER, DB_PASSWORD, DB_NAME

def data_exists_in_db(filename, table_name):
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()

        # Checking if data exists in the specified table
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE filename = %s", (filename,))
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count > 0
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        return False

class TestUploadCsvToSql(unittest.TestCase):
    def test_upload_csv_to_sql(self):
        # Testing data
        filename = "hired_employees_test.csv"
        table_name = "hired_employees"
        # Inserting test data into the Cloud SQL database
        upload_csv_to_sql(filename, table_name)
        # Checking if data exists in the database
        self.assertTrue(data_exists_in_db(filename, table_name))

if __name__ == '__main__':
    unittest.main()
