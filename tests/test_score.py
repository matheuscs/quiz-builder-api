import pytest

from app.db import schemas
from app.helpers.math import calculate_scores


def test_quiz1():
    questions = [
        schemas.QuestionMock(
            id=4,
            single_correct_answer=False,
            answers=[
                schemas.AnswerMock(id=21, is_correct=False),
                schemas.AnswerMock(id=9, is_correct=False),
                schemas.AnswerMock(id=11, is_correct=True),
                schemas.AnswerMock(id=29, is_correct=True),
                schemas.AnswerMock(id=18, is_correct=True)
            ]
        ),
        schemas.QuestionMock(
            id=27,
            single_correct_answer=False,
            answers=[
                schemas.AnswerMock(id=2, is_correct=True),
                schemas.AnswerMock(id=40, is_correct=True),
                schemas.AnswerMock(id=32, is_correct=True),
                schemas.AnswerMock(id=60, is_correct=True),
                schemas.AnswerMock(id=57, is_correct=False)
            ]
        ),
        schemas.QuestionMock(
            id=79,
            single_correct_answer=True,
            answers=[
                schemas.AnswerMock(id=7, is_correct=False),
                schemas.AnswerMock(id=49, is_correct=True),
                schemas.AnswerMock(id=41, is_correct=False),
                schemas.AnswerMock(id=52, is_correct=False),
                schemas.AnswerMock(id=62, is_correct=False)
            ]
        ),
    ]
    user_answers = {
        # multiple
        21: True, 9: False, 11: True, 29: True, 18: False,
        # multiple
        2: True, 40: False, 32: False, 60: True, 57: False,
        # single
        7: False, 49: False, 41: True, 52: False, 62: False
    }
    assert calculate_scores(questions, user_answers) == (
        [
            {'question_id': 4, 'score': 16},
            {'question_id': 27, 'score': 50},
            {'question_id': 79, 'score': -100}
        ],
        -11
    )


def test_quiz_invalid_key():
    questions = [
        schemas.QuestionMock(
            id=1,
            single_correct_answer=False,
            answers=[
                schemas.AnswerMock(id=11, is_correct=True),
                schemas.AnswerMock(id=12, is_correct=False)
            ]
        )
    ]
    user_answers = {11: False, 15: False}
    with pytest.raises(KeyError, match="12"):
        calculate_scores(questions, user_answers)


def test_quiz_invalid_multiple_correct_answer():
    questions = [
        schemas.QuestionMock(
            id=1,
            single_correct_answer=True,
            answers=[
                schemas.AnswerMock(id=11, is_correct=True),
                schemas.AnswerMock(id=12, is_correct=False)
            ]
        )
    ]
    user_answers = {11: True, 12: True}
    with pytest.raises(
            ValueError,
            match="Only one correct answer is allowed for a single "
                  "correct answer question"):
        calculate_scores(questions, user_answers)
