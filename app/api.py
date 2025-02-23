from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base_dir)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Malt Scraper API",
    description="API for scraping Malt freelancer profiles",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class BaseResponse(BaseModel):
    status: bool
    message: str

class SuccessResponse(BaseResponse):
    data: Dict[str, Any]

class ErrorResponse(BaseResponse):
    error: str
    details: Optional[Dict[str, Any]] = None

# Routes
@app.get("/api/v1/health", response_model=SuccessResponse)
async def health_check():
    """Health check endpoint."""
    return SuccessResponse(
        status=True,
        message="Service is healthy",
        data={"timestamp": "2025-02-23T13:51:02Z"}
    )

@app.get("/api/v1", response_model=SuccessResponse)
async def root():
    """Root endpoint."""
    return SuccessResponse(
        status=True,
        message="Welcome to Malt Scraper API",
        data={
            "version": "1.0.0",
            "docs_url": "/api/v1/docs",
            "redoc_url": "/api/v1/redoc"
        }
    )

@app.get("/api/v1/profil", response_model=SuccessResponse)
async def profil(url: str):
    try:
        assert url.startswith("https://malt.fr/profile/")
        
        """Scrape Malt freelancer profile."""
        scraper = MaltScraper(headless=False, profil_url=url)
        result = scraper.extract_profile_data()
        return SuccessResponse(
            status=True,
            message="Profile scraped successfully",
            data=result
        )
        
    except AssertionError:
        raise HTTPException(status_code=400, detail="Invalid URL")
