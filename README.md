# Grievance Bot

A backend-powered AI-driven grievance redressal bot that manages complaints, integrates with a database, and provides automated responses through API endpoints.

---

## 🚀 Features
- Complaint registration and management system  
- AI-driven agent logic for handling grievances  
- REST API for integration with frontend or third-party apps  
- Database layer for storing user complaints and system logs  
- Easy setup with Python  

---

## 🗂 Project Structure
```
grievance_botfinal/
│── app.py                # Main entry point (Streamlit frontend)
│── setup_and_run.py      # Script to initialize and run backend
│── requirements.txt      # Dependencies
│── backend/
│   ├── api/
│   │   └── api_server.py # API endpoints
│   ├── database/
│   │   └── database.py   # Database models & connection
│   └── agents/
│       └── agents.py     # AI grievance handling logic
```

---

## ⚙️ Installation

Clone this repository:
```bash
git clone <repo_url>
cd grievance_botfinal
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

Run the APP backend and frontend:
```bash
python setup_and_run.py
```

Or directly:
```bash
python backend/api/api_server.py
```

Run the chatbot frontend:
```bash
streamlit run app.py
```

---

## 📦 Database
Configurations are handled in:
```
backend/database/database.py
```
Update DB credentials (MongoDB or other database) as required.

---

## 🤖 Agents
Defined in:
```
backend/agents/agents.py
```
Extendable for different types of complaint handling logic.

---

## 📝 API Endpoints

Base URL (default): `http://127.0.0.1:8000/`

- **POST** `/api/register_complaint` → Register a new complaint  
- **GET** `/api/complaint_status/{id}` → Fetch complaint status by complaint ID  
- **GET** `/api/complaints_by_mobile/{mobile}` → Fetch all complaints linked to a mobile number  

---

## 📌 Requirements
- Python 3.8+  
- FastAPI, Uvicorn, Streamlit (see `requirements.txt`)  
- MongoDB (or configure your preferred DB)  

---

## 🛠 Future Enhancements
- More complaint management endpoints (update, delete)  
- Frontend integration (React/Angular/Vue)  
- Authentication & user management  
- Advanced NLP for grievance categorization  
