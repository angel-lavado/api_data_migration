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
        
