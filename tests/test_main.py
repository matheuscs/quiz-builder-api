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

auth_headers = ''
last_quiz_id = 0
last_question_id = 0
last_answer_id = 0
EMAIL = f'tester{random()}@testing.com'
PASS = 'secret'


def test_get_current_user_unauthorized():
    response = client.get("/users")
    assert response.status_code == 401


def test_create_user():
    response = client.post(
        "/users",
        json={
            "email": EMAIL,
            "password": PASS
        },
    )
    assert response.status_code == 200, response.text


def test_authenticate():
    response = client.post(
        '/token',
        data={'username': EMAIL, 'password': PASS}
    )
    assert response.status_code == 200

    global auth_headers
    auth_headers = {
        'Authorization': f'Bearer {response.json()["access_token"]}',
        'Accept': 'application/json'
    }


def test_get_user():
    response = client.get("/users", headers=auth_headers)
    assert response.status_code == 200


def test_create_quiz_for_user():
    response = client.post(
        f'/users/quiz',
        json={
            "title": f"Incredible Quiz No. {random()}"
        },
        headers=auth_headers
    )
    assert response.status_code == 200, response.text

    global last_quiz_id
    last_quiz_id = response.json()['id']


def test_get_quizes():
    response = client.get(f'/quizes', headers=auth_headers)
    assert response.status_code == 200, response.text


def test_quiz_by_id():
    response = client.get(f"/quizes/{last_quiz_id}", headers=auth_headers)
    assert response.status_code == 200, response.text


def test_quiz_not_found():
    response = client.get("/quizes/-1", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Quiz not found"}


def test_update_quiz():
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
           {"detail": "Quiz can't be activated"}


def test_create_questions_for_quiz():
    global last_question_id
    for i in range(11):
        response = client.post(
            f'/quizes/{last_quiz_id}/question',
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


def test_question_not_found():
    response = client.get("/questions/-1", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_create_answers_for_questions():
    global last_answer_id
    for i in range(6):
        response = client.post(
            f'/questions/{last_question_id}/answer',
            json={
                "description": f"Answer {random()}",
                "is_correct": "true"
            },
            headers=auth_headers
        )
        if i < 5:
            assert response.status_code == 200, response.text
            last_answer_id = response.json()['id']
        else:
            assert response.status_code == 409, response.text
            assert response.json() == \
                   {"detail": "Maximum answers for a question reached: 5"}


def test_answer_not_found():
    response = client.get("/answers/-1", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Answer not found"}


def test_delete_answer():
    response = client.delete(f"/answers/{last_answer_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_not_found_answer():
    response = client.delete(f"/answers/-1", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Answer not found"}


def test_delete_question():
    response = client.delete(f"/questions/{last_question_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_not_found_question():
    response = client.delete(f"/questions/-1", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_delete_quiz():
    response = client.delete(f"/quizes/{last_quiz_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_not_found_quiz():
    response = client.delete(f"/quizes/-1", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Quiz not found"}
