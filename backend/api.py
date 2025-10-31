
from fastapi import FastAPI, HTTPException, status, Path
from typing import Optional
from pydantic import BaseModel

import uvicorn
import psycopg2

app = FastAPI()

connection = psycopg2.connect(
    database="my_db",
    user="postgres",
    password="mypassword",
    host="database",
    port=5432
)

cursor = connection.cursor()

# Sending queries to the database and error handling
def sql_fetch(query: str, parameters: tuple):
    try:
        cursor.execute(query, parameters)
        return cursor.fetchall()
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error with fetch - psycopg2: {e}")

def sql_exec(query: str, parameters: tuple):
    try:
        cursor.execute(query, parameters)
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error with exec - psycopg2: {e}")


# Data Models
class User(BaseModel):
    name: str
    age: int

class UpdateUser(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None


# Root
@app.get("/")
def root():
    return {"message":"hello world"}

# Get user
@app.get("/users/{user_id}")
def get_user(user_id: int = Path(..., description="ID toget", gt=0, lt=100)):
    record = sql_fetch(query="SELECT name, age FROM users WHERE id = %s;", parameters=(user_id,))

    if len(record) == 0: # User does not exist
        raise HTTPException(status_code=404, detail="User not found")

    user = User(
        name=record[0][0],
        age=record[0][1]
    )

    return user

# Create a user
@app.post("/users/{user_id}", status_code=status.HTTP_201_CREATED)
def create_user(user_id: int, user: User):
    record = sql_fetch(query="SELECT 1 FROM users WHERE id = %s;", parameters=(user_id,))

    if len(record) != 0: # User does exist
        raise HTTPException(status_code=400, detail="User already exists")

    sql_exec(query="INSERT INTO users (id, name, age) VALUES (%s, %s, %s);", parameters=(user_id, user.name, user.age))

    return user

# Update a user
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UpdateUser):
    record = sql_fetch(query="SELECT 1 FROM users WHERE id = %s;", parameters=(user_id,))

    if len(record) == 0: # User does not exist
        raise HTTPException(status_code=400, detail="User is not here")
    
    if user.name is not None:
        sql_exec(query="UPDATE users SET name = %s;", parameters=(user.name,))
    if user.age is not None:
        sql_exec(query="UPDATE users SET age = %s;", parameters=(user.age,))

    return get_user(user_id=user_id)

# Delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    record = sql_fetch(query="SELECT 1 FROM users WHERE id = %s;", parameters=(user_id,))

    if len(record) == 0: # User does not exist
        raise HTTPException(status_code=400, detail="User is not here")

    user = get_user(user_id=user_id)
    sql_exec(query="DELETE FROM users WHERE id = %s;", parameters=(user_id,))

    return {"message": "User has been deleted", "deleted_user": user}

# Search for a user
@app.get("/users/search/")
def search_by_name(name: Optional[str] = None):
    if not name:
        return {"message": "Name parameter is required"}

    record_id = sql_fetch(query="SELECT id FROM users WHERE name = %s", parameters=(name,)) 

    if len(record_id) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user(user_id=record_id[0][0]) 

# Display all users
@app.get("/users/all/")
def get_all_users():
    users = {}
    all_users = sql_fetch(query="SELECT id, name, age FROM users;", parameters=None)

    for record in all_users:
        users[record[0]] = User(
            name=record[1],
            age=record[2]
        )
    
    return users

if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8000)
