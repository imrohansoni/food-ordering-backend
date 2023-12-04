from utils import get_variables, set_variables
import requests


def test_create_product():
    auth_token = get_variables().get("auth_token")
    res = requests.post("http://localhost:5000/api/v1/products", json={
        "name": "vegetarian pizza",
        "description": "this is the pizza description",
        "category_id": "656ddc90e9ea8b3c90371b5b",
        "type": "veg",
        "image_url": "pizza.image",
        "customizable": True
    }, headers={
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()

    print(data)
    product_data = data.get("data")
    assert res.status_code == 201


def test_get_products():
    auth_token = get_variables().get("auth_token")
    result = requests.get("http://localhost:5000/api/v1/products", headers={
        "content-type": "application/json",
        "authorization": f"Bearer {auth_token}"
    })

    data = result.json()
    print(data)
    assert result.status_code == 200
