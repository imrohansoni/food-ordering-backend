import requests
from utils import set_variables, get_variables
from sys import argv

BASE_URL = "http://localhost:5000/api/v1"

headers = {
    "content-type": "application/json"
}


def test_create_category():
    auth_token = get_variables().get("auth_token")

    res = requests.post(f"{BASE_URL}/categories", json={
        "category_name": "pizza",
        "description": "best pizzas"
    }, headers={
        **headers,
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_delete_category():
    category_id = "656c0dcc6fd8641239652940"
    auth_token = get_variables().get("auth_token")

    res = requests.delete(f"{BASE_URL}/categories/{category_id}", headers={
        **headers,
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_update_category():
    category_id = "656c0dcc6fd8641239652940"
    auth_token = get_variables().get("auth_token")

    res = requests.patch(f"{BASE_URL}/categories/{category_id}",
                         json={
                             "category_name": "pizza"
                         }, headers={
            **headers,
            "authorization": f"Bearer {auth_token}"
        })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_get_categories():
    print(argv[0])
    auth_token = get_variables().get("auth_token")

    res = requests.get(f"{BASE_URL}/categories", headers={
        **headers,
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200
