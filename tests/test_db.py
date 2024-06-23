from datetime import datetime, timedelta
import random

from app import db

TEST_USERNAME = 'lorenpeve10'

def _get_number_of_records(username: str) -> int:
    with db.POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUnT(*) FROM weightlifting
            WHERE user_id = (%s)
            """, (username,)
        )
        count = cur.fetchone()[0]
    return count


def test_get_exercises():
    exercises = db.get_list_of_exercises(TEST_USERNAME)    
    assert 'deadlift' in exercises
    
def test_add_exercise():

    # Before adding an exercise
    exercise_name = 'test12345'
    exercises = db.get_list_of_exercises(TEST_USERNAME)
    assert exercise_name not in exercises

    # Add an exercise
    db.add_exercise(
        user_id=TEST_USERNAME,
        exercise=exercise_name,
        weight=100,
        reps=10,
        date=datetime.now().date() + timedelta(days=1),
        after_wod=False,
        comment='test comment'
    )

    exercises = db.get_list_of_exercises(TEST_USERNAME)
    assert exercise_name in exercises

    # Delete newly inserted exercise
    exercises = db.get_weightlifting_records(TEST_USERNAME, exercise_name)
    id_to_delete = exercises[0]['id']
    db.delete_exercise([id_to_delete])

def test_delete_exercise():

    exercises = db.get_list_of_exercises(TEST_USERNAME)
    name = random.choice(exercises)

    n_old = _get_number_of_records(TEST_USERNAME)
    assert n_old > 0
    
    exercises = db.get_weightlifting_records(TEST_USERNAME, name)
    ids = [exercise['id'] for exercise in exercises[:3]]

    db.delete_exercise(ids)
    
    n_new = _get_number_of_records(TEST_USERNAME)
    assert n_new == n_old - len(ids)

def test_get_weightlifting_records():

    records = db.get_weightlifting_records(TEST_USERNAME, 'deadlift')
    assert len(records) > 0
    assert records[0]['exercise'] == 'deadlift'