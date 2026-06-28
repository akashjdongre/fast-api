from pydantic import BaseModel,Field
from typing import Optional,Literal
from db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime,timezone  

class Movies(Base):
    __tablename__="movies"
    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    genre = Column(String(100))
    release_year = Column(Integer)
    rating = Column(Float)
    status = Column(String(10))
    update_date = Column(DateTime)

class MovieCreate(BaseModel):
    movie_title:str=Field(...,min_length=1,max_length=100,description="Movie Title/Name")
    genre:Optional[str] = Field(None, max_length=300)
    release_year:int=Field(...,ge=1900, le=9999,description="Movie Release Year")
    rating:float=Field(...,description="Movie Rating")
    status:Literal['0', '1']


class MovieResp(BaseModel):
    movie_title: str
    genre: str
    release_year: int
    rating: float
    updated_at: Optional[datetime] = None

class RespMovieCreate(BaseModel):
    message: str
    data: Optional[list[MovieResp]]=None

class RespMovieGet(BaseModel):
    count: int
    data: list[MovieResp]

class UpdMovieData(BaseModel):
    movie_title: Optional[str]= Field(None)
    genre: Optional[str]= Field(None)
    release_year: Optional[int]= Field(None)
    rating: Optional[float]= Field(None)

class RespMovieUpdate(BaseModel):
    message: str
    data: MovieResp

class RespMovieDelete(BaseModel):
    success: bool
    message: str
    id: int