import bcrypt
from dotenv import load_dotenv
import os
from psycopg_pool import ConnectionPool

load_dotenv(override=True)

conn_string = (
    f"host={os.getenv('DB_HOST')} "
    f"port={os.getenv('DB_PORT')} "
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASSWORD')}"
)

POOL = ConnectionPool(
    conninfo=conn_string,
    open=True,
    min_size=3
    )

def set_inputs_to_none_if_empty(func):
    """Decorator that sets empty strings to None in function arguments."""
    def wrapper(*args, **kwargs):

        modified_args = tuple(None if arg == '' else arg for arg in args)
        modified_kwargs = {key: (None if value == '' else value) for key, value in kwargs.items()}
        result = func(*modified_args, **modified_kwargs)
        
        return result
    return wrapper
    
def get_list_of_exercises(username: str) -> list[str]:
    """Return a list of exercises for a given user."""

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT exercise FROM weightlifting
            WHERE user_id = %s
            """, (username,)               
        )

    return [s[0] for s in sorted(cur.fetchall())]

@set_inputs_to_none_if_empty
def add_exercise(
    user_id: str,
    exercise: str,
    weight: float,
    reps: int,
    date: str,
    after_wod: bool,
    comment: str
) -> None:
    
    """Add an exercise to the database for a given user."""

    assert float(weight)
    assert int(reps)

    with POOL.connection() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO weightlifting
            (user_id, exercise, weight, reps, date, after_wod, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, exercise, weight, reps, date, after_wod, comment)
        )

def delete_exercise(ids: list[int], user: str) -> None:
    """Delete an exercise from the database."""

    s = ''
    for i in ids:
        s+= str(i) + ', '

    query = f"DELETE FROM weightlifting WHERE id in ({s[:-2]}) AND user_id = '{user}'"

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(query)

def get_weightlifting_records(
        username: str,
        exercise: str,
        reps: int = None
    ) -> list[dict]:

    """Queries the database for weightlifting records for a given user and exercise."""

    if reps is not None and len(str(reps)) > 0:
        with POOL.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, user_id, exercise, weight, reps, date, after_wod, comment
                FROM weightlifting
                WHERE user_id = %s AND exercise = %s AND reps = %s
                ORDER BY date DESC
                """, (username, exercise, reps)
            )
    else:
        with POOL.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, user_id, exercise, weight, reps, date, after_wod, comment
                FROM weightlifting
                WHERE user_id = %s AND exercise = %s
                ORDER BY date DESC
                """, (username, exercise)
            )

    out = []
    for record in cur:
        out.append({
            'id': record[0],
            'user_id': record[1],
            'exercise': record[2],
            'weight': str(record[3]).replace('.0', ''),
            'reps': record[4],
            'date': record[5],
            'after_wod': record[6],
            'comment': record[7]
        })
    return out

def add_user(username: str, password: str, email: str) -> None:
    """Add a user to the database."""

    hashed_password = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()).decode('utf-8')

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (username, password, email)
            VALUES (%s, %s, %s)
            """, (username, hashed_password, email)
        )

def delete_user(username: str) -> None:
    """Delete a user from the database."""

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = %s", (username,))

def user_exists(username: str) -> bool:
    """Check if the user exists in the database."""

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT username FROM users WHERE username = %s", (username,))
        return cur.fetchone() is not None
    
def email_exists(email: str) -> bool:
    """Check if the email exists in the database."""

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT email FROM users WHERE email = %s", (email,))
        return cur.fetchone() is not None

def login_credentials_exists(username: str, password: str) -> bool:
    """Check if the user exists in the database."""
    
    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT password FROM users
            WHERE username = %s
            """, (username,)               
        )

        stored_hashed_password  = cur.fetchone()

    if stored_hashed_password is None:
        raise Exception("User does not exist.")

    if stored_hashed_password :
        password_match = bcrypt.checkpw(
            password.encode('utf-8'),
            stored_hashed_password[0].encode('utf-8')
        )

        if password_match:
            return True
        else:
            raise Exception('Password does not match')

    raise Exception('Condition not designed for')