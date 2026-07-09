from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime

class RespNewUser(BaseModel):
    message: str
    id: int

class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    image_url: str | None = None
    
    class Config:
        from_attributes = True

class RespAllPRoducts(BaseModel):
    source: str
    total: int
    page: int
    limit: int
    results: List[ProductResponse]