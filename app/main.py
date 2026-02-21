from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes
from app.routes import bus_routes
from app.routes import routes_routes
from app.routes import trip_routes

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(bus_routes.router)
app.include_router(routes_routes.router)
app.include_router(trip_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/") 
def home() : 
    return {"message" : "This is home page"}