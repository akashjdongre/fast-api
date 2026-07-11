from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime
from fastapi import UploadFile, File, Form

#----- BaseModel is designed for validating JSON payloads. 
#----- Form() and File() are dependency markers intended for endpoint parameters.

class RespNewUser(BaseModel):
    message: str
    id: int

class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class RespSingleProducts(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    image_url: str | None = None

class ProductResponse(BaseModel):
    page: int
    limit: int
    results: List[RespSingleProducts]

class RespAllPRoducts(BaseModel):
    source: str
    data: List[ProductResponse]
    count: int

class RespProductDelete(BaseModel):
    message: str
    product_info: RespSingleProducts