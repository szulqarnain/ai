# Use the official Python 3.5 slim image
FROM python:3.5-slim

# Install necessary packages
RUN apt-get update && apt-get install -y tzdata \
    && apt-get install -y --no-install-recommends \
            curl \
            build-essential \
            libsqlite3-dev \
            libreadline-dev \
            libssl-dev \
            ca-certificates \
            openssl \
            cmake \
            libpng-dev \
            libfreetype6-dev \
            libfontconfig1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY flask-import/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY ./flask-import .
COPY ./neo4j-import /neo4j-import

# Expose the port
EXPOSE 8888

# Command to run your webserver
CMD ["python", "webserver.py"]
