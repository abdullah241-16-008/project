from fastapi import APIRouter
from fastapi.responses import JSONResponse
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
