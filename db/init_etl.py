import bcrypt
from dotenv import load_dotenv
import json
import os
import psycopg
from psycopg import OperationalError

load_dotenv(override=True)

def create_connection() -> psycopg.connection:
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Connection to PostgreSQL DB successful")
        return conn
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        raise e

def init_schema() -> None:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;


    CREATE TABLE users (
        username VARCHAR(50) PRIMARY KEY,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );            

    CREATE TABLE weightlifting (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL,
        exercise VARCHAR(40) NOT NULL,
        weight NUMERIC(4, 1) NOT NULL CHECK (weight >= 0),
        reps INT NOT NULL CHECK (reps > 0),
        date DATE NOT NULL,
        after_wod BOOLEAN DEFAULT false,
        comment VARCHAR(100) DEFAULT NULL,
        
        FOREIGN KEY (user_id) references users(username)
    );
                
    CREATE TABLE amrap (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL,
        wod VARCHAR(200) NOT NULL,
        timecap INT NOT NULL, -- minutes
        rounds_plus_reps VARCHAR(10) NOT NULL,
        date DATE NOT NULL,
        comment VARCHAR(100) DEFAULT NULL,
        
        FOREIGN KEY (user_id) references users(username),
        CONSTRAINT valid_amrap_score CHECK (rounds_plus_reps ~ '^[0-9]{1,}(\+[0-9]+){0,}$')
    );
                
    CREATE TABLE emom (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL,
        wod VARCHAR(200) NOT NULL,
        duration INT NOT NULL, -- minutes
        date DATE NOT NULL,
        comment VARCHAR(100) DEFAULT NULL,
        
        FOREIGN KEY (user_id) references users(username)
    );

    CREATE TABLE rounds_for_time (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL,
        wod VARCHAR(200) NOT NULL,
        rounds INT NOT NULL,
        time NUMERIC(5, 2) NOT NULL,  -- minutes
        date DATE NOT NULL,
        comment VARCHAR(100) DEFAULT NULL,
        
        FOREIGN KEY (user_id) references users(username)
    );
                
    CREATE TABLE hero_and_benchmarks_wods (
        user_id VARCHAR(20),
        name VARCHAR(20),
        description VARCHAR(200) NOT NULL,
        
        PRIMARY KEY(user_id, name),
        FOREIGN KEY (user_id) references users(username)
    );

    CREATE TABLE hero_and_benchmarks (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL,
        name VARCHAR(20) NOT NULL,
        time NUMERIC(5, 2) NOT NULL,  -- minutes
        date DATE NOT NULL,
        comment VARCHAR(100) DEFAULT NULL,
        
        FOREIGN KEY (user_id) references users(username),
        FOREIGN KEY (user_id, name) references hero_and_benchmarks_wods(user_id, name)
    );

    CREATE TABLE cardio (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL,
        activity VARCHAR(20) NOT NULL,
        distance_km NUMERIC NOT NULL, -- kilometers
        time NUMERIC NOT NULL,
        date DATE NOT NULL,
        comment VARCHAR(100) DEFAULT NULL,
        
        FOREIGN KEY (user_id) references users(username)
    );
    """)
    conn.commit()
    conn.close()

def add_users(username: str, password: str, email: str):
    conn = create_connection()
    cur = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    hashed_email = bcrypt.hashpw(email.encode(), bcrypt.gensalt()).decode('utf-8')
    cur.execute("""
    INSERT INTO users (username, email, password) VALUES 
    (%s, %s, %s)
    """, (username, hashed_email, hashed_password))
    conn.commit()
    conn.close()


if __name__ == "__main__":

    init_schema()

    USERNAME = os.getenv('TEST_USERNAME')
    USERPASSWORD = os.getenv('TEST_USER_PASSWORD')
    add_users(USERNAME, USERPASSWORD, 'example@gmail.com')

    with open("db/init_records.json", "r") as f:
        data = json.load(f)
        data = [(
            USERNAME,
            record['exercise'],
            record['weight'],
            record['reps'],
            record['date'],
            record.get('after_wod'),
            record.get('comment')
        )
        for record in data
        ]

        conn = create_connection()
        cur = conn.cursor()
        cur.executemany("""
        INSERT INTO weightlifting (user_id, exercise, weight, reps, date, after_wod, comment)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)

        conn.commit()
    conn.close()