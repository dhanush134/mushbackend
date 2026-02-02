from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Mushroom Farming Optimization API",
    description="RESTful API for mushroom farming data management and AI-powered insights",
    version="1.0.0"
)

# CORS configuration
# Allow all origins for GitHub Pages deployment
# Since frontend doesn't use credentials, this is safe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
from routes import batches, observations, harvests, insights

app.include_router(batches.router)
app.include_router(observations.router)
app.include_router(harvests.router)
app.include_router(insights.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Mushroom Farming Optimization API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
