FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY apps/api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole api directory
COPY apps/api ./apps/api

# Set PYTHONPATH so absolute imports work
ENV PYTHONPATH=/app/apps

# Run uvicorn
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
