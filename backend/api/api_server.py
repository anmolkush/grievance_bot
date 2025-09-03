from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from backend.database.database import Database , Complaint
import random
import string
from datetime import datetime

app = FastAPI()
db = Database()

class ComplaintRequest(BaseModel):
    name: str
    mobile: str
    complaint_details: str

class ComplaintResponse(BaseModel):
    complaint_id: str
    message: str

class StatusResponse(BaseModel):
    complaint_id: str
    status: str
    created_at: datetime
    updated_at: datetime

def generate_complaint_id():
    return f"CMP-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

@app.post("/api/register_complaint", response_model=ComplaintResponse)
async def register_complaint(complaint: ComplaintRequest):
    try:
        complaint_id = generate_complaint_id()
        
        complaint_data = {
            "complaint_id": complaint_id,
            "name": complaint.name,
            "mobile": complaint.mobile,
            "complaint_details": complaint.complaint_details,
            "status": "In Progress"
        }
        
        db.create_complaint(complaint_data)
        
        return ComplaintResponse(
            complaint_id=complaint_id,
            message=f"Complaint registered successfully with ID: {complaint_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/complaint_status/{complaint_id}", response_model=StatusResponse)
async def get_complaint_status(complaint_id: str):
    complaint = db.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return StatusResponse(
        complaint_id=complaint.complaint_id,
        status=complaint.status,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at
    )

@app.get("/api/complaints_by_mobile/{mobile}")
async def get_complaints_by_mobile(mobile: str):
    complaints = db.get_complaints_by_mobile(mobile)
    return [
        {
            "complaint_id": c.complaint_id,
            "status": c.status,
            "details": c.complaint_details,
            "created_at": c.created_at
        }
        for c in complaints
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)