# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Copy gunicorn configuration file to /app
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Run app.py when the container launches using gunicorn with the config file
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "3", "--timeout", "30", "--worker-class", "gthread"]
