# Environment variables & configuration settings
PROJECT_ID ='dlake-dev-12ab'
CLOUD_SQL_CONNECTION_NAME = 'dlake-dev-12ab:us-central1:external_data_sources'
GCS_BUCKET_NAME = 'it-analytics-from-external-sources-12345'
DB_USER = 'angel.lavado'
DB_PASSWORD = '123456'
DB_NAME = 'external_data_sources'

TABLE_CONFIGS = {
    'hired_employees.csv': {
        'field_mappings': {
            'id': 'id',
            'name': 'name',
            'datetime': 'datetime',
            'department_id': 'department_id',
            'job_id': 'job_id',

        }
    },
    'departments.csv': {
        'field_mappings': {
            'id': 'id',
            'department': 'department',
        }
    },
    'jobs.csv': {
        'field_mappings':{
            'id': 'id',
            'job': 'job'
        }
    }
}