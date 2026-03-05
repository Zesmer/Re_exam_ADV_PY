from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, customer, admin

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce API Service",
    description="Complete E-commerce API with Customer & Admin endpoints",
    version="1.0.0"
)

# CORS Middleware (Allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to E-commerce API",
        "docs": "/docs",
        "version": "1.0.0"
    }