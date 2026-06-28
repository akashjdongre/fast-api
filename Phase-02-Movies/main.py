from fastapi import FastAPI,APIRouter,HTTPException,Depends,status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from db import get_db
from schema import Movies,RespMovieCreate,MovieCreate,RespMovieGet,MovieResp,UpdMovieData,RespMovieUpdate,RespMovieDelete
from datetime import datetime

app = FastAPI(
    title="Movies Database",
    description="Simple CRUD Operation on DB",
    version="1.0.0"
)
#--------------------------- GET ALL MOVIES ---------------------------#

@app.get("/movies", response_model=RespMovieGet)
def get_movies(
     db: Session = Depends(get_db)
):
    movies = db.query(Movies).all()
    movie_list = [
        {
            "movie_title": movie.title,
            "genre": movie.genre,
            "release_year": movie.release_year,
            "rating": movie.rating,
        }
        for movie in movies
    ]
    return {
        "count": len(movie_list),
        "data": movie_list,
    }

#-------------------------GET MOVIES BY ID ---------------------------#

@app.get("/movies/{movie_id}", response_model=MovieResp)
def get_movie(
    movie_id:int,
    db: Session = Depends(get_db)
):
    get_movie = (
        db.query(Movies)
        .filter(Movies.movie_id == movie_id)
        .first()
    )
    if get_movie:
        movie_data = {
            "movie_title": get_movie.title,
            "genre": get_movie.genre,
            "release_year": get_movie.release_year,
            "rating": get_movie.rating,
        }
        return movie_data
    else:
        raise HTTPException(status_code=404, detail="Movie not found")

#------------------------- CREATE MOVIES ---------------------------#

@app.post("/movies", response_model=RespMovieCreate, status_code=status.HTTP_201_CREATED)
def create_movies(
    form_input: MovieCreate,
    db: Session = Depends(get_db)
):  
    chk_movie = (
        db.query(Movies)
        .filter(Movies.title == form_input.movie_title)
        .first()
    )
 
    if chk_movie:
        return {
            "message": f"Movie '{form_input.movie_title}' already exists",
        }
    
    movie_data = Movies(
        title=form_input.movie_title,
        genre=form_input.genre,
        release_year=form_input.release_year,
        rating=form_input.rating,
        status=form_input.status
    )
    # Add to session and commit
    db.add(movie_data)
    db.commit()
    db.refresh(movie_data)

    movie_response_data = [
        {
            "movie_title": movie_data.title,
            "genre": movie_data.genre,
            "release_year": movie_data.release_year,
            "rating": movie_data.rating
        }
    ]

    return_json = {
        "message": "Movie Data Added successfully.",
        "data": movie_response_data
    }

    return return_json

#-------------------------- UPDATE MOVIE DATA ---------------------#

@app.put("/movies/{movie_id}", response_model=RespMovieUpdate)
def update_movie_data(
    movie_id: int,
    m_data: UpdMovieData,
    db: Session = Depends(get_db)
):
    get_movie = (
        db.query(Movies)
        .filter(Movies.movie_id == movie_id)
        .first()
    )
    if not get_movie:
        raise HTTPException(status_code=404, detail="Movie not found for Id : {movie_id}")
    
    if m_data.movie_title is not None:
        get_movie.title = m_data.movie_title
    
    if m_data.genre is not None:
        get_movie.genre = m_data.genre
    
    if m_data.release_year is not None:
        get_movie.release_year = m_data.release_year
    
    if m_data.rating is not None:
        get_movie.rating = m_data.rating
    
    get_movie.update_date = datetime.now()

    db.commit()
    db.refresh(get_movie)

    movie_response_data = {
            "movie_title": get_movie.title,
            "genre": get_movie.genre,
            "release_year": get_movie.release_year,
            "rating": get_movie.rating
        }
    

    return {
        "message": "Movie Data updated successfully",
        "data": movie_response_data
    }

#-------------------------- DELETE MOVIE DATA ---------------------#

@app.delete("/movies/{movie_id}",response_model=RespMovieDelete)
def update_movie_data(
    movie_id: int,
    db: Session = Depends(get_db)
):
    get_movie = (
        db.query(Movies)
        .filter(Movies.movie_id == movie_id)
        .first()
    )
    if not get_movie:
        raise HTTPException(status_code=404, detail=f"Movie not found for Id : {movie_id}")
    
    delete_movie = (
        db.query(Movies)
        .filter(Movies.movie_id == movie_id)
        .delete()
    )
    db.commit()

    if delete_movie:
        return{
            "success": True,
            "message" : f"Movie {get_movie.title} deleted successfully.",
            "id" : movie_id
        }