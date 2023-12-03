import requests
from utils import set_variables, get_variables

BASE_URL = "http://localhost:5000/api/v1"

headers = {
    "content-type": "application/json"
}


def test_send_code():
    mobile_number = "8851138132"

    res = requests.post(f"{BASE_URL}/auth/send-code", json={
        "mobile_number": mobile_number
    }, headers=headers)

    data = res.json()

    set_variables(data.get("data"))

    assert res.status_code == 200


def test_login():
    env = get_variables()
    code = 1234

    res = requests.post(f"{BASE_URL}/auth/login", json={
        "mobile_number": env.get("mobile_number"),
        "hash": env.get("hash"),
        "code": code,
        "expires_at": env.get("expires_at")
    }, headers=headers)

    data = res.json()
    assert res.status_code == 200
    set_variables(data.get("data"))


def test_send_code_update_mobile():
    mobile_number = "9650173057"
    auth_token = get_variables().get("auth_token")

    res = requests.post(f"{BASE_URL}/auth/update-mobile/send-code", json={
        "mobile_number": mobile_number,
    }, headers={
        **headers,
        "authorization": f"Bearer {auth_token}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200
    set_variables(data.get("data"))


def test_update_mobile():
    env = get_variables()
    code = 9019

    res = requests.post(f"{BASE_URL}/auth/update-mobile", json={
        "mobile_number": env.get("mobile_number"),
        "hash": env.get("hash"),
        "code": code,
        "expires_at": env.get("expires_at")
    }, headers={
        **headers,
        "authorization": f"Bearer {env.get("auth_token")}"
    })

    data = res.json()
    print(data)
    assert res.status_code == 200
