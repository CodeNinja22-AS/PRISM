FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY apps/api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole api directory contents into /app
COPY apps/api .

# Run uvicorn directly from the app root
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
