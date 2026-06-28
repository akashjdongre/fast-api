from fastapi import FastAPI
from routes.todos import router as todo_router

app = FastAPI(
    title="Todo Api",
    description="Simple to do REST API with Fast API",
    version="1.0.0"
)

app.include_router(todo_router)

@app.get("/", tags=["Health"])
def root():
    return {"message":"Todo App is Running."}