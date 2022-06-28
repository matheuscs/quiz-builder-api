from random import random
from fastapi.testclient import TestClient
from app.api import app, get_db
from app.db.database import TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
token = ''
auth_headers = ''
email = ''
last_user_id = 0
last_quiz_id = 0
last_question_id = 0


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


def test_create_user():
    global email
    email = f"newtester{random()}@testing.com"
    response = client.post(
        "/users",
        json={
            "email": email,
            "password": "abc123"
        },
    )
    assert response.status_code == 200, response.text

    global last_user_id
    last_user_id = response.json()['id']


def test_authenticate():
    response = client.post(
        '/token',
        data={'username': email, 'password': 'abc123'}
    )
    assert response.status_code == 200

    global token
    token = response.json()["access_token"]

    global auth_headers
    auth_headers = {'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'}


def test_alive_secure():
    response = client.get("/alive_secure", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"msg": "i'm alive and secure"}


def test_get_all_users():
    response = client.get("/users", headers=auth_headers)
    assert response.status_code == 200


def test_create_quiz_for_user():
    response = client.post(
        f'/user/{last_user_id}/quiz',
        json={
            "title": f"Incredible Quiz No. {random()}"
        },
        headers=auth_headers
    )
    assert response.status_code == 200, response.text

    global last_quiz_id
    last_quiz_id = response.json()['id']


def test_get_quiz_by_id():
    response = client.get(f'/quiz/{last_quiz_id}', headers=auth_headers)
    assert response.status_code == 200, response.text


def test_get_quizes_for_user():
    response = client.get(f'/user/{last_user_id}/quizes', headers=auth_headers)
    assert response.status_code == 200, response.text


def test_update_quiz():
    response = client.put(
        f'/quizes/{last_quiz_id}',
        json={
            "title": f"Incredible Quiz No. {random()}",
            "is_active": "true"
        },
        headers=auth_headers
    )
    assert response.status_code == 200, response.text

    response = client.put(
        f'/quizes/{last_quiz_id}',
        json={
            "title": f"Incredible Quiz No. {random()}",
            "is_active": True
        },
        headers=auth_headers
    )
    assert response.status_code == 405, response.text
    assert response.json() == \
           {"detail": "You can't update a published quiz."}


def test_create_questions_for_quiz():
    global last_question_id
    for i in range(11):
        response = client.post(
            f'/quiz/{last_quiz_id}/question',
            json={
                "description": f"Question {random()}",
                "single_correct_answer": "true"
            },
            headers=auth_headers
        )
        if i < 10:
            assert response.status_code == 200, response.text
            last_question_id = response.json()['id']
        else:
            assert response.status_code == 409, response.text
            assert response.json() == \
                   {"detail": "Maximum questions for a quiz reached: 10"}


def test_create_answers_for_questions():
    for i in range(6):
        response = client.post(
            f'/question/{last_question_id}/answer',
            json={
                "description": f"Question {random()}",
                "is_correct": "true"
            },
            headers=auth_headers
        )
        if i < 5:
            assert response.status_code == 200, response.text
        else:
            assert response.status_code == 409, response.text
            assert response.json() == \
                   {"detail": "Maximum answers for a question reached: 5"}
