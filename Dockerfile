# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port
EXPOSE 8000

# Command to start the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
