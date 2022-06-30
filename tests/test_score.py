import pytest
from app.helpers.math import calculate_scores


def test_quiz1():
    questions = [
        {
            "single_correct_answer": False,
            "id": 4,
            "answers": [
                {
                    "id": 21,
                    "is_correct": False
                },
                {
                    "id": 9,
                    "is_correct": False
                },
                {
                    "id": 11,
                    "is_correct": True
                },
                {
                    "id": 29,
                    "is_correct": True
                },
                {
                    "id": 18,
                    "is_correct": True
                }
            ]
        },
        {
            "single_correct_answer": False,
            "id": 27,
            "answers": [
                {
                    "id": 2,
                    "is_correct": True
                },
                {
                    "id": 40,
                    "is_correct": True
                },
                {
                    "id": 32,
                    "is_correct": True
                },
                {
                    "id": 60,
                    "is_correct": True
                },
                {
                    "id": 57,
                    "is_correct": False
                }
            ]
        },
        {
            "single_correct_answer": True,
            "id": 79,
            "answers": [
                {
                    "id": 7,
                    "is_correct": False
                },
                {
                    "id": 49,
                    "is_correct": True
                },
                {
                    "id": 41,
                    "is_correct": False
                },
                {
                    "id": 52,
                    "is_correct": False
                },
                {
                    "id": 62,
                    "is_correct": False
                }
            ]
        },

    ]

    user_answers = {
        # multiple
        21: True,
        9: False,
        11: True,
        29: True,
        18: False,

        # multiple
        2: True,
        40: False,
        32: False,
        60: True,
        57: False,

        # single
        7: False,
        49: False,
        41: True,
        52: False,
        62: False
    }
    assert calculate_scores(questions, user_answers) == (
        [
            {'question_id': 4, 'score': 16},
            {'question_id': 27, 'score': 50},
            {'question_id': 79, 'score': -100}],
        {'quiz_score': -11}
    )


def test_quiz_invalid_key():
    questions = [
        {
            "single_correct_answer": False,
            "id": 1,
            "answers": [
                {
                    "id": 11,
                    "is_correct": True
                },
                {
                    "id": 12,
                    "is_correct": False
                }
            ]
        }
    ]

    user_answers = {
        11: True,
        15: False
    }
    with pytest.raises(KeyError, match="12"):
        calculate_scores(questions, user_answers)


def test_quiz_invalid_multiple_correct_answer():
    questions = [
        {
            "single_correct_answer": True,
            "id": 1,
            "answers": [
                {
                    "id": 11,
                    "is_correct": True
                },
                {
                    "id": 12,
                    "is_correct": False
                }
            ]
        }
    ]

    user_answers = {
        11: True,
        12: True
    }
    with pytest.raises(ValueError,
                       match="Only one correct answer is allowed for a single "
                             "correct answer question"):
        calculate_scores(questions, user_answers)
