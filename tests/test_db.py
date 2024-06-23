from app import db



def test_get_exercises():

    exercises = db.get_exercises('lorenpeve10')
    print(exercises)