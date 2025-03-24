import mysql.connector
import hashlib

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sri@sql49",
        database="trading_platform"
    )
    conn.autocommit = True
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        return "✅ User registered successfully!"
    except mysql.connector.Error as err:
        return f"❌ Error: {err}"
    finally:
        cursor.close()
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT user_id, password FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        stored_user_id, stored_password = result
        hashed_input_password = hash_password(password)
        if hashed_input_password == stored_password:
            cursor.close()
            conn.close()
            return stored_user_id
    cursor.close()
    conn.close()
    return None
#hi
