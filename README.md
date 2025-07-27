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
if you use Docker, change "DATABASE_HOST" in .env from "27.0.0.1" to "db"

---

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

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# in separate terminal
celery -A hrgf worker --loglevel=info

## Setup With Docker

docker-compose up --build

## inside the container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic ## if needed

