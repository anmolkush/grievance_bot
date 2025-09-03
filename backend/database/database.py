from pymongo import MongoClient
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
import certifi

load_dotenv()

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        schema.update(type="string")
        return schema

class Complaint(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    complaint_id: str
    name: str
    mobile: str
    complaint_details: str
    status: str = "In Progress"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Database:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI not found in environment variables")
        
        # Connect to MongoDB Atlas with SSL certificate
        self.client = MongoClient(
            mongodb_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        try:
            self.client.admin.command('ping')
            print("Connected to MongoDB Atlas")
        except Exception as e:
            print(f"Failed to connect to MongoDB Atlas: {e}")
            raise
        
        self.db = self.client[os.getenv("DATABASE_NAME", "grievance_db")]
        self.complaints = self.db.complaints
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            self.complaints.create_index("complaint_id", unique=True)
            self.complaints.create_index("mobile")
            self.complaints.create_index("created_at")
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
        
    def create_complaint(self, complaint_data: Dict[str, Any]) -> Complaint:
        complaint_data["created_at"] = datetime.now()
        complaint_data["updated_at"] = datetime.now()
        result = self.complaints.insert_one(complaint_data)
        complaint_data["_id"] = result.inserted_id
        return Complaint(**complaint_data)
    
    def get_complaint_by_id(self, complaint_id: str) -> Optional[Complaint]:
        complaint = self.complaints.find_one({"complaint_id": complaint_id})
        if complaint:
            return Complaint(**complaint)
        return None
    
    def get_complaints_by_mobile(self, mobile: str) -> List[Complaint]:
        complaints = self.complaints.find({"mobile": mobile}).sort("created_at", -1)
        return [Complaint(**complaint) for complaint in complaints]
    
    def update_complaint_status(self, complaint_id: str, status: str) -> Optional[Complaint]:
        result = self.complaints.find_one_and_update(
            {"complaint_id": complaint_id},
            {"$set": {"status": status, "updated_at": datetime.now()}},
            return_document=True
        )
        if result:
            return Complaint(**result)
        return None
    
    def __del__(self):
        """Close MongoDB connection when object is destroyed"""
        if hasattr(self, 'client'):
            self.client.close()