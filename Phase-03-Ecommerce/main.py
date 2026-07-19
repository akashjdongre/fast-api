from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routes import auth, products, orders, websocket

#---------Module for rate limiting ---------------#
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.limiter import limiter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="E-Commerce API", version="3.0.0")

#-----------------------------------------------------#

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#-----------------------------------------------------#

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(websocket.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "E-Commerce API running 🚀"}