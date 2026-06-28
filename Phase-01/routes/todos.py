# routes/todos.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from models import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["Todos"])

# In-memory storage
todos_db: dict[int, dict] = {}
counter: int = 0
 
# CREATE — POST /todos
@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    global counter
    counter += 1
    new_todo = {"id": counter, **todo.model_dump()}
    todos_db[counter] = new_todo
    return new_todo


# READ ALL — GET /todos
@router.get("/", response_model=List[TodoResponse])
def get_all_todos():
    return list(todos_db.values())


# READ ONE — GET /todos/{id}
@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    todo = todos_db.get(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )
    return todo


# UPDATE — PUT /todos/{id}
@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, updated: TodoUpdate):
    todo = todos_db.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    
    update_data = updated.model_dump(exclude_unset=True)  # only fields sent by client
    todo.update(update_data)
    todos_db[todo_id] = todo
    return todo


# DELETE — DELETE /todos/{id}
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    del todos_db[todo_id]