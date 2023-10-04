# app.py
from flask import Flask, request, jsonify
import os
from google.cloud import storage
import psycopg2

app = Flask(__name__)

# Importing configuration settings from the config.py file
from config import (
    PROJECT_ID,
    CLOUD_SQL_CONNECTION_NAME,
    GCS_BUCKET_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    TABLE_CONFIGS
)

# Connecting to the Cloud SQL database
def get_db_connection():
    connection_name = CLOUD_SQL_CONNECTION_NAME
    unix_socket = f'/cloudsql/{connection_name}'
    
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        unix_socket=unix_socket
    )
    return conn

# Uploading CSV files from GCS to Cloud SQL
def upload_csv_to_sql(filename, table_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    table_config = TABLE_CONFIGS.get(table_name)
    
    if table_config:
        with storage.Client().bucket(os.environ['GCS_BUCKET_NAME']).blob(filename).open("r") as file:
            next(file)  # Skip the header
            for line in file:
                data = line.strip().split(",")

                # Mapping CSV columns to table columns using the field_mappings
                mapped_data = [data[csv_column] for csv_column, table_column in table_config['field_mappings'].items()]

                # Building the SQL query dynamically based on table and field mappings
                insert_query = f"INSERT INTO {table_name} ({','.join(table_config['field_mappings'].values())}) VALUES ({','.join(['%s'] * len(mapped_data))})"

                cursor.execute(insert_query, mapped_data)

        conn.commit()
        conn.close()
    else:
        # Handling cases where the provided table_name is not found
        print(f"Table configuration for {table_name} not found.")


# API route to upload CSV files and perform migration
@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'object_path' not in request.form or 'table_name' not in request.form:
        return jsonify({"Message": "Invalid request"}), 400

    object_path = request.form['object_path']
    table_name = request.form['table_name']

    if not object_path:
        return jsonify({"Message": "No GCS object path provided"}), 400

    try:
        # Downloading the CSV file from GCS
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(os.environ['GCS_BUCKET_NAME'])
        blob = bucket.blob(object_path)

        # Specifying the local filename where the GCS object will be downloaded
        local_filename = os.path.join("temp/", os.path.basename(object_path))

        blob.download_to_filename(local_filename)

        # Uploading the downloaded CSV file to Cloud SQL with the specified table name
        upload_csv_to_sql(local_filename, table_name)

        return jsonify({"Message": "File from GCS uploaded and data migrated successfully"}), 200
    except psycopg2.Error as db_error:
        return jsonify({"Error Message": f"Database Error: {db_error}"}), 500
    except IOError as io_error:
        return jsonify({"Error Message": f"IO Error: {io_error}"}), 500
    except Exception as e:
        return jsonify({"Error Message": f"An unexpected error occurred: {str(e)}"}), 500


# API route for the first SQL query requirement (Cloud SQL)
@app.route('/requirement1', methods=['GET'])
def requirement1():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql_query = """
            SELECT 
                d.department,
                j.job,
                COUNTIF(MONTH(he.datetime) BETWEEN 1 AND 3) AS Q1,
                COUNTIF(MONTH(he.datetime) BETWEEN 4 AND 6) AS Q2,
                COUNTIF(MONTH(he.datetime) BETWEEN 7 AND 9) AS Q3,
                COUNTIF(MONTH(he.datetime) BETWEEN 10 AND 12) AS Q4   
            FROM hired_employees AS he
            LEFT JOIN departments AS d
                ON he.department_id = d.id
            LEFT JOIN jobs AS j
                ON he.job_id = j.id
            WHERE 
                YEAR(he.hired_date) = '2021'
            GROUP BY d.department, j.job
            ORDER BY d.department, j.job;
            """
        cursor.execute(sql_query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(results), 200

    except psycopg2.Error as db_error:
        return jsonify({"Error Message": f"Database Error: {db_error}"}), 500
    except Exception as e:
        return jsonify({"Error Message": f"An unexpected error occurred: {str(e)}"}), 500

# API route for the second SQL query requirement (Cloud SQL)
@app.route('/requirement2', methods=['GET'])
def requirement2():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql_query = """
            WITH hired_employees AS (

            SELECT 
                d.id,
                d.department,
                COUNT(he.id) AS hired	
                COUNT(CASE WHEN YEAR(datetime) = '2021' THEN he.id END) AS hired_2021
            FROM hired_employees AS he
            LEFT JOIN departments AS d
            ON he.department_id = d.id
            GROUP BY 
                d.id, d.department

            ), mean_employees_by_department AS (

            SELECT MEAN(hired_2021) AS mean_by_department
            FROM hired_employees

            )
            SELECT 
                id, department, hired 
            FROM hired_employees
            WHERE hired > (SELECT mean_by_department FROM mean_employees_by_department)
            ORDER BY hired DESC
        """
        cursor.execute(sql_query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(results), 200

    except psycopg2.Error as db_error:
        return jsonify({"Error Message": f"Database Error: {db_error}"}), 500
    except Exception as e:
        return jsonify({"Error Message": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':

    app.run(debug=True)

        
