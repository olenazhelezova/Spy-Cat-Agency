#  🙀 Spy Cat Agency Management System (SCAMS)


A backend system for managing secret feline agents, their missions, and field targets. Built with **Django REST Framework**, this project demonstrates state management, relational modeling, and business logic enforcement.

## Core Technologies
* **Backend:** Python 3.13+ / Django 6.0+
* **API:** Django REST Framework (DRF)
* **Documentation:** OpenAPI / Swagger via `drf-spectacular`
* **Validation:** TheCatAPI (External API integration)

## Requirements

- Python 3.13+ (or whichever version you use locally)
- pip3
- Recommended: create and use a virtualenv

## Setup

### Clone the repository
```bash
git clone https://github.com/olenazhelezova/Spy-Cat-Agency.git
cd Spy-Cat-Agency
```

### Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Apply migrations and create a superuser:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
> **Note**: Creating a superuser is optional.
You only need it if you want to log into the Django admin panel.


### Start the development server:
```bash
python manage.py runserver
```

## Database

The project ships with `db.sqlite3` for development and testing.

## API Endpoints

Available endpoints (router + a small embedded route):

- `GET /cats/` — List all spy cats
- `POST /cats/` — Create a new spy cat (Name, Years of Experience, Breed, Salary; Breed is validated via TheCatAPI)
- `GET /cats/{id}/` — Retrieve a single spy cat 
- `PUT/PATCH /cats/{id}/` — Update a cat's information (e.g., Salary)
- `DELETE /cats/{id}/` — Remove a spy cat from the system

- `GET /missions/` — List all missions in the system  
- `POST /missions/` — Create a new mission along with its associated targets
- `GET /missions/{id}/` — Retrieve detailed information about a specific mission, including its targets 
- `PUT/PATCH /missions/{id}/` — Update mission details (e.g. assign a cat) or modify target information
- `DELETE /missions/{id}/` — Delete a mission. Deleting a mission is blocked if a cat is assigned.

Targets are handled nested under missions. The project currently exposes a nested partial-update route:

- `PATCH /missions/{mission_pk}/targets/{pk}` — Update a target’s notes or completion status within a mission. Notes cannot be updated if either the target or the mission is completed

## Example requests

### Create a Spy Cat
> Note: The breed must match a valid feline breed from TheCatAPI.
```bash
curl -X POST http://127.0.0.1:8000/api/cats/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Plyamka",
    "years_of_experience": 5,
    "breed": "Persian",
    "salary": "500.00"
  }'
```

### Create a Mission (with 1-3 Targets)
Missions must be created with at least one target in an atomic payload.
```bash
curl -X POST http://127.0.0.1:8000/api/missions/ \
  -H "Content-Type: application/json" \
  -d '{
    "targets": [
      {"name": "Eat all fish", "country": "Greece", "notes": "Investigate the best taverna"},
      {"name": "Drink all milk", "country": "UK", "notes": "Find near Tesco"}
    ]
  }'
```

### Assign a Cat to a Mission
Use the ID of the cat and the specific assignment action endpoint.
```bash
curl -X PATCH http://127.0.0.1:8000/api/missions/1/ \
  -H "Content-Type: application/json" \
  -d '{"cat": 1}'
```

### Update Target Notes
This only works if the target is not complete and the mission is not complete.
```bash
curl -X PATCH http://127.0.0.1:8000/api/missions/1/targets/1 \
  -H "Content-Type: application/json" \
  -d '{"notes": "Ooooops"}'
```

### Mark target as completed
This only works if the target is not complete and the mission is not completed yet.
```bash
curl -X PATCH http://127.0.0.1:8000/api/missions/1/targets/1 \
  -H "Content-Type: application/json" \
  -d '{"is_complete": true}'  
```

## OpenAPI Schema

A generated OpenAPI schema is available at `openapi/schema.yml`. The codebase uses `drf-spectacular`; see `api/views.py` where schema hints are applied for certain update/partial_update operations.

To regenerate the schema (if configured), you might run:
```bash
# example; depends on project setup
python manage.py spectacular --file openapi/schema.yml
```

Interactive web interface is also available at `%hostname%/api/schema/swagger/`
## Postman Collection

You can import and test the API using this Postman collection:

[Spy Cat Agency API Collection](https://www.postman.com/supply-geologist-26255502/workspace/cats/collection/22111702-f5fc6b94-6b53-48ff-8dac-38f1404acd5d?action=share&creator=22111702)

## Automated Testing

Run tests with:
```bash
python manage.py test
```
