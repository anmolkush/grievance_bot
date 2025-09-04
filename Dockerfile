# Use Python 3.10 slim
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all project files
COPY . .

# Expose ports for Streamlit and FastAPI
EXPOSE 8501
EXPOSE 8001

RUN chmod +x start.sh


# Run startup script
CMD ["bash", "start.sh"]
