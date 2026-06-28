from pydantic import BaseModel, Field
from typing import Optional

class TodoCreate(BaseModel):
    title:str=Field(...,min_length=1,max_length=50,description="Title of Todo")
    description:Optional[str]=Field(None, max_length=100)
    completed:bool=False

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool