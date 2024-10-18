FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install numpy and joblib explicitly
RUN pip install --no-cache-dir numpy==1.19.2 joblib==1.0.1

# Install other dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose the service port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

