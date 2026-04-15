from fastapi import APIRouter
from fastapi.responses import JSONResponse
import bcrypt
from .db_connection import get_db_connection

router = APIRouter()


@router.get("/all-users")
async def get_all_users():
    """Fetch all users for dashboard"""
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        cursor.close()
        db.close()
        
        return {
            "users": [
                {"user_id": user[0], "username": user[1]}
                for user in users
            ]
        }
    
    except Exception as e:
        cursor.close()
        db.close()
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})


@router.get("/public-key/{user_id}")
async def get_public_key(user_id: int):
    """Fetch user's public key for encryption"""
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT public_key FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if not result:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        return {"user_id": user_id, "public_key": result[0]}

    except Exception as e:
        cursor.close()
        db.close()
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})


@router.post("/private-key")
async def get_private_key(data: dict):
    """Fetch user's private key after password verification"""
    user_id = data.get("user_id")
    password = data.get("password")

    if not user_id or not password:
        return JSONResponse(status_code=400, content={"message": "user_id and password required"})

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT private_key, password FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if not result:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        private_key_pem, stored_password = result
        if isinstance(stored_password, str):
            stored_password = stored_password.encode()

        if not bcrypt.checkpw(password.encode(), stored_password):
            return JSONResponse(status_code=401, content={"message": "Wrong password"})

        return {"user_id": user_id, "private_key": private_key_pem}

    except Exception as e:
        cursor.close()
        db.close()
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})
