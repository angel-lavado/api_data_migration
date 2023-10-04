# API FOR DATA MIGRATION (PostgresSQL to GCP CloudSQL)

## PROJECT DESCRIPTION
After an extensive analysis of Advanced Analytics team, they have decided to migrate data from on-premise database (PostgresSQL) to on-cloud database in GCP (Cloud SQL). This migration will support a more scalable solution.

The main purpose of this project is to build & deploy an API that migrates transaction data from PostgresSQL to Cloud SQL.

Tables were already extracted and load it into a GCP Cloud Storage bucket.

Main functionalities:
- Receive historical data from CSV files in Cloud Storage
- Upload these files to Cloud SQL
- Be able to insert batch transactions (1 up to 1000 rows) with one request
- Provide an Endpoint that returns the number of employees hired for each job and department in 2021 divided by quarter. The table must be ordered alphabetically by department and job. (Requirement 1)
- Provide Endpoint that returns the list of ids, name and number of employees hired of each department that hired more employees than the mean of employees hired in 2021 for all the departments, ordered by the number of employees hired (descending). (Requirement 2)


## INSTALLATION INSTRUCTIONS
1. Build the Docker Image using the command: 
```docker build -t api_image:latest```
This command builds an image named "api_image" with a specified tag.

2. Push the Docker Image: Push the Docker image to your Google Containter Registry (GCR) repository. First, authenticate with GCR using gcloud: 
```gcloud auth configure-docker```

Then, tag and push the image:
```docker tag api_image:tag gcr.io/dlake-dev-12ab/api_image:latest```
```docker push gcr.io/dlake-dev-12ab/api_image:latest```

3. Create a GKE Cluster: Set up a GKE cluster where the Docker container will run. You can use the gcloud command or the Google Cloud Console to create a cluster.

4. Deploy the Application: Create a Kubernetes Deployment and Service configuration (YAML). Deploy the application using kubectl apply:
```kubectl apply -f api_deployment.yaml```

5. Expose the Application: Use a Kubernetes Service (LoadBalancer or NodePort) to expose the application to the internet or other services.

6. Access the Application: Once the external IP address is assigned to the LoadBalancer, you can access your application.

## USAGE
Make sure you deployed Docker container in GKE and have an URL where your API is hosted.

1. Upload CSV files from GCS to Cloud SQL
```curl -X POST -F "object_path=it-analytics-from-external-sources-12345/hired_employees.csv" -F "table_name=hired_employees" http://api-url/upload ```

2. End-point to get 1st SQL query statement
Make a GET request to the /requirement1 endpoint of your API. It will return data in JSON format.
```curl http://api-url/requirement1```

3. End-point to get 2nd SQL query statement
Make a GET request to the /requirement2 endpoint of your API.  It will return data in JSON format.
```curl http://api-url/requirement2```

4. API testing
To run the tests, execute test_runner.py scripts as part of the CI/CD pipeline when needed.


