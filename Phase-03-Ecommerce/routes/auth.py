from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from core.auth import hash_password, verify_password, create_access_token
from response.response import RespNewUser,NewUser

from core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=RespNewUser, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,  # accept either JSON body or query params
    db: Session = Depends(get_db)
    ):  
    try:
        body = await request.json()
    except Exception:
        body = {}
    params = dict(request.query_params)
    data = {**body, **params}

    form_input = NewUser(**data)

    email_exist = db.query(User).filter(User.email == form_input.email).first()
    if email_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User Email : {form_input.email} already registered")

    user_data = User(
        name=form_input.name,
        email=form_input.email,
        password=hash_password(form_input.password)   # never store plain text
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {"message": "User created", "id": user_data.id}
 

@router.post("/login")
@limiter.limit("5/minute")  # Limit to 5 login attempts per minute
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}