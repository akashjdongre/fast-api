from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routes import auth, products, orders, websocket

#---Use this database connection (engine) to create the tables.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce API", version="3.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(websocket.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "E-commerce API running 🚀"}