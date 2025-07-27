# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput

# Copy project
COPY . .

# Port (optional, mainly for local dev)
EXPOSE 8000

# Run migrations and start server
CMD ["gunicorn", "hrgf.wsgi:application", "--bind", "0.0.0.0:8000"]
