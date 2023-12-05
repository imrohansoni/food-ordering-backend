from utils import get_variables, set_variables
import requests

BASE_URL = "http://localhost:5000/api/v1"


def test_create_option_group():
    variables = get_variables()
    product_id = variables.get("product_id")
    auth_token = variables.get("auth_token")

    res = requests.post(f"{BASE_URL}/products/{product_id}/option-group", json={
        "title": "sizes",
        "sub_title": "select one of these sizes",
        "type": "size"
    }, headers={
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_create_option():
    variables = get_variables()
    product_id = variables.get("product_id")
    auth_token = variables.get("auth_token")

    res = requests.post(f"{BASE_URL}/products/{product_id}/options", json={
        "value": "medium",
        "price": 333,
        "discount": 10,
        "available": False
    }, headers={
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_delete_option():
    variables = get_variables()
    product_id = variables.get("product_id")
    auth_token = variables.get("auth_token")

    res = requests.delete(f"{BASE_URL}/products/{product_id}/options"
                          "/656ea405b669288ca435b5e1", headers={
                              "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_update_option():
    variables = get_variables()
    product_id = variables.get("product_id")
    auth_token = variables.get("auth_token")

    res = requests.patch(
        f"{BASE_URL}/products/{product_id}/options/656ea3bb39c1c89b3ba0e3a3",
        json={
            "available": False,
            "price": 99
        },
        headers={
            "authorization": f"Bearer {auth_token}"
        })

    data = res.json()
    print(data)
    assert res.status_code == 200


def test_get_options():
    variables = get_variables()
    product_id = variables.get("product_id")
    auth_token = variables.get("auth_token")

    res = requests.get(
        f"{BASE_URL}/products/{product_id}/options",
        headers={
            "authorization": f"Bearer {auth_token}"
        })

    data = res.json()
    print(data)
    assert res.status_code == 200
