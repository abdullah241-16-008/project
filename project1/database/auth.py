from fastapi import APIRouter
from fastapi.responses import JSONResponse
import bcrypt
from .db_connection import get_db_connection
import mysql.connector

router = APIRouter()

@router.post("/register")
async def register(data: dict):
    username = data["username"]
    password = data["password"]

    # 1. Hash the password before saving
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # 2. Save to MySQL
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed)
        )
        db.commit()
        user_id = cursor.lastrowid
        cursor.close()
        db.close()
        return {"message": "Registration successful!", "user_id": user_id, "username": username}

    except mysql.connector.IntegrityError:
        # This runs if username already exists
        cursor.close()
        db.close()
        return {"message": "Username already taken!"}
    except Exception as e:
        cursor.close()
        db.close()
        return {"message": f"Error: {str(e)}"}


@router.post("/login")
async def login(data: dict):
    username = data["username"]
    password = data["password"]

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    # No matching user
    if user is None:
        return JSONResponse(status_code=401, content={"message": "Wrong username or password."})

    user_id, stored = user[0], user[1]

    # MySQL may return TEXT/VARCHAR as str; bcrypt expects bytes
    if isinstance(stored, str):
        stored = stored.encode()

    if stored and bcrypt.checkpw(password.encode(), stored):
        return {"message": "Login successful!", "username": username, "user_id": user_id}

    return JSONResponse(status_code=401, content={"message": "Wrong username or password."})
