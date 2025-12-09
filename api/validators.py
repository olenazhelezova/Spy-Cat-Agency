import requests
from rest_framework.exceptions import ValidationError

CAT_API_URL = "https://api.thecatapi.com/v1/breeds"


def validate_cat_breed(breed_value):
    try:
        response = requests.get(url=CAT_API_URL)
        response.raise_for_status()
        breeds_data = response.json()
        valid_breeds = [b['name'].lower() for b in breeds_data]
        if breed_value.lower() not in valid_breeds:
            raise ValidationError(f"Invalid breed: {breed_value}.")
    except requests.RequestException as e:
        raise ValidationError(
            f"Could not validate breed due to API error: {e}")
