# HRGF Backend

This is the backend for the HRGF e-commerce project task built using Django REST Framework.

## Project URL

> https://github.com/arshak2002/hrgf_backend

---

## Requirements

- Python 3.9+
- pip
- PostgreSQL
- Docker (optional)
- Celery for asynchronous/background tasks (for send email to order placed user)
- Git

## Base URL
http://localhost:8000/api/

## Swagger
http://localhost:8000/api/swagger

## Docker
if you use Docker, change "DATABASE_HOST" in .env from "127.0.0.1" to "db"

---

## Advanced Features
sending Email to user when order placed
Receipt download option in 'orders' menu item for user

## Clone the Project

```bash
git clone https://github.com/arshak2002/hrgf_backend.git
cd hrgf_backend

## Setup Without Docker

python -m env env
source env/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

## Mac
brew install redis
brew services start redis

# for pdf generation (WeasyPrint) Mac
brew install cairo pango gdk-pixbuf libffi 

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# in separate terminal
celery -A hrgf worker --loglevel=info

## Setup With Docker

# if your using docker
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

docker-compose up --build

## inside the container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic ## if needed

