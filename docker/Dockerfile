# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install Node.js and npm for Vercel CLI
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install Vercel CLI globally
RUN npm install -g vercel

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Set environment variables
ENV FLASK_APP=api/index.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run"] 