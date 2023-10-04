# Setting Python runtime 
FROM python:3.8

# Setting the working directory in the container
WORKDIR /app

# Copying the current directory contents into the container
COPY . /app

# Installing necessary dependencies
RUN pip install -r requirements.txt

# Exposing the port
EXPOSE 5000

# Running your application
CMD ["python", "app.py"]
