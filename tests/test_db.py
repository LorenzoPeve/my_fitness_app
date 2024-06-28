from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import psycopg
import random

from app import db

load_dotenv(override=True)

TEST_USERNAME = os.getenv('TEST_USERNAME')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')

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
    db.delete_exercise([id_to_delete], TEST_USERNAME)

def test_delete_exercise():

    exercises = db.get_list_of_exercises(TEST_USERNAME)
    name = random.choice(exercises)

    n_old = _get_number_of_records(TEST_USERNAME)
    assert n_old > 0
    
    exercises = db.get_weightlifting_records(TEST_USERNAME, name)
    ids = [exercise['id'] for exercise in exercises[:3]]

    db.delete_exercise(ids, TEST_USERNAME)
    
    n_new = _get_number_of_records(TEST_USERNAME)
    assert n_new == n_old - len(ids)

def test_add_exercise_multiple_times():

    # Before adding an exercise
    exercise_name = 'test12345'
    exercises = db.get_list_of_exercises(TEST_USERNAME)
    assert exercise_name not in exercises

    N = 5
    # Add an exercise
    db.add_exercise_multiple_times(
        N,
        user_id=TEST_USERNAME,
        exercise=exercise_name,
        weight=100,
        reps=10,
        date=datetime.now().date() + timedelta(days=1),
        after_wod=False,
        comment=''
    )

    exercises = db.get_list_of_exercises(TEST_USERNAME)
    assert exercise_name in exercises

    # Delete newly inserted exercise
    exercises = db.get_weightlifting_records(TEST_USERNAME, exercise_name)

    ids = [exercise['id'] for exercise in exercises[:N]]
    db.delete_exercise(ids, TEST_USERNAME)

    id_to_delete = exercises[0]['id']
    db.delete_exercise([id_to_delete], TEST_USERNAME)

def test_get_weightlifting_records():

    records = db.get_weightlifting_records(TEST_USERNAME, 'deadlift')
    assert len(records) > 0
    assert records[0]['exercise'] == 'deadlift'

    reps_scheme = [record['reps'] for record in records]
    assert len(set(reps_scheme)) > 1 # All records, regardless of reps are returned

def test_get_weightlifting_records_invalid_ex():

    records = db.get_weightlifting_records(TEST_USERNAME, 'no_such_exercise')
    assert len(records) == 0

def test_get_weightlifting_records_with_reps():

    records = db.get_weightlifting_records(TEST_USERNAME, 'deadlift', 1)
    assert len(records) > 0
    assert records[0]['exercise'] == 'deadlift'

    reps_scheme = [record['reps'] for record in records]
    assert len(set(reps_scheme)) == 1 # All records, regardless of reps are returned

def test_add_user():
    username = 'test_user'
    password = 'test_password'
    email = 'test_email'
    db.add_user(username, password, email)
    assert db.user_exists(username)

def test_add_user_exception():
    username = 'test_user'
    password = 'test_password'
    email = 'test_email'
    try:
        db.add_user(username, password, email)
    except psycopg.errors.UniqueViolation as e:
        assert 'duplicate key value violates unique constraint' in str(e)
    else:
        raise AssertionError('UniqueViolation not raised')

def test_delete_user():
    username = 'test_user'
    password = 'test_password'
    assert db.user_exists(username)
    db.delete_user(username)
    assert not db.user_exists(username)

def test_user_exists():
    username = 'test_user'
    password = 'test_password'
    email = 'admin@admin.com'

    assert not db.user_exists(username)
    db.add_user(username, password, email)
    assert db.user_exists(username)
    db.delete_user(username)

def test_email_exists():
    username = 'test_user'
    password = 'test_password'
    email = 'admin@admin.com'
    db.add_user(username, password, email)
    assert db.email_exists(email)
    assert not db.email_exists('this_does_not_exist@gmail.com')
    db.delete_user(username)

def test_login_credentials_exist():

    assert db.login_credentials_exists(TEST_USERNAME, TEST_USER_PASSWORD)
    
    try:
        db.login_credentials_exists('wrong_user', 'wrong_password')
    except Exception as e:
        assert 'User does not exist' in str(e)
    else:
        raise AssertionError('AssertionError not raised')
    
    try:
        db.login_credentials_exists(TEST_USERNAME, 'wrong_password')
    except Exception as e:
        assert 'Password does not match' in str(e)
    else:
        raise AssertionError('AssertionError not raised')