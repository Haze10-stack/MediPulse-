from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
import os

# Add the current directory to the path so Python can find your module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the OPDSystemManager class from test.py
try:
    from test import OPDSystemManager
except ImportError:
    print("Error: Could not import OPDSystemManager from test.py.")
    print("Make sure your file is correctly named and contains the OPDSystemManager class.")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="OPD Time Slot API",
    description="API for finding available time slots in the Outpatient Department system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
CSV_PATH = "Patients_Records2.csv"
GEMINI_API_KEY = "AIzaSyAHOaOT-dx28PBk46PBpgvbj9ocDjMAlZ4"  # Replace with your actual API key if needed

# Initialize the OPDSystemManager at startup
opd_manager = OPDSystemManager(CSV_PATH, GEMINI_API_KEY)

# Define the data model for patient details
class PatientDetails(BaseModel):
    department: str = Field(..., description="Medical department name")
    patient_type: str = Field(..., description="Type of patient (e.g., Critical, Regular, Follow-up)")
    symptoms: str = Field(default="Not specified", description="Patient symptoms")

@app.get("/")
async def root():
    """Welcome endpoint with basic information"""
    return {
        "message": "OPD Appointment Scheduler API",
        "endpoints": {
            "time_slots": "/available-time-slots",
            "departments": "/departments"
        }
    }

@app.get("/departments")
async def get_departments():
    """Get list of all available departments"""
    return {"departments": opd_manager.all_departments}

@app.post("/available-time-slots")
async def get_available_time_slots(patient: PatientDetails):
    """
    Get available time slots based on patient details
    
    This endpoint returns recommended appointment slots based on department, 
    patient type, and symptoms, along with AI triage information when available.
    """
    try:
        slots = opd_manager.recommend_time_slots(patient.dict())
        return slots
    except Exception as e:
        logging.error(f"Error generating time slots: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting available time slots: {str(e)}")

# Add this if you need to run the server directly with "python main.py"
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)