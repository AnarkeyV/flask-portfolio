# Use official Python image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

# Don't copy sensitive files
# (handled by .dockerignore)

# Set environment variables
ENV FLASK_APP=flask_app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Run the app
CMD ["flask", "run", "--host=0.0.0.0"]
