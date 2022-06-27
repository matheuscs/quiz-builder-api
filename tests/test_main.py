from fastapi.testclient import TestClient
from app.api import app


client = TestClient(app)
token = client.post('/token',
                    data={'username': 'math@email.com', 'password': '123'}
                    ).json()["access_token"]
auth_headers = {'Authorization': f'Bearer {token}',
                'Accept': 'application/json'}


def test_alive():
    response = client.get("/alive")
    assert response.status_code == 200
    assert response.json() == {"msg": "i'm alive"}


def test_alive_secure_unauthorized():
    response = client.get("/alive_secure")
    assert response.status_code == 401


def test_get_all_users_unauthorized():
    response = client.get("/users")
    assert response.status_code == 401


def test_authenticate():
    response = client.post(
        '/token',
        data={'username': 'math@email.com', 'password': '123'}
    )
    assert response.status_code == 200


def test_alive_secure():
    response = client.get("/alive_secure", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"msg": "i'm alive and secure"}


def test_get_all_users():
    response = client.get("/users", headers=auth_headers)
    assert response.status_code == 200
