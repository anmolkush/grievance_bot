import subprocess
import sys
import time
import os
from dotenv import load_dotenv

def setup_and_run():
    print(" Setting up the Grievance Management Chatbot...")
    
    # Install requirements using the install script
    print("\n📦 Installing required packages...")
    try:
        # Try using the install script first
        if os.path.exists("install_packages.py"):
            subprocess.check_call([sys.executable, "install_packages.py"])
        else:
            # Fallback to requirements.txt
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("\n  Some packages failed to install. Trying alternative method...")
        # Try installing without version constraints
        packages = [
            "streamlit", "langchain", "langchain-community", "langchain-openai",
            "pymongo", "python-dotenv", "fastapi", "uvicorn", "requests",
            "openai", "pydantic", "certifi", "dnspython"
        ]
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except:
                print(f"Warning: Could not install {package}")
    
    # Load existing .env if exists
    load_dotenv()
    
    # Check if .env exists and has required variables
    if not os.path.exists(".env"):
        print("\n Creating .env file...")
        print("\n  You need a MongoDB Atlas connection string.")
        print("Format: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/")
        
        mongodb_uri = input("\nEnter your MongoDB Atlas URI: ").strip()
        openai_key = input("Enter your OpenAI API key: ").strip()
        
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={openai_key}\n")
            f.write(f"MONGODB_URI={mongodb_uri}\n")
            f.write("DATABASE_NAME=grievance_db\n")
        
        # Reload environment variables
        load_dotenv(override=True)
    
    # Check MongoDB Atlas connection
    print("\n🔍 Checking MongoDB Atlas connection...")
    try:
        from pymongo import MongoClient
        import certifi
        
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            print(" MongoDB URI not found in .env file!")
            return
        
        # Use certifi for SSL certificates (required for Atlas)
        client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
        
        # Test connection
        client.admin.command('ping')
        print(" Connected to MongoDB Atlas successfully!")
        
        # List databases to verify connection
        db_names = client.list_database_names()
        print(f" Available databases: {', '.join(db_names[:3])}...")
        
    except Exception as e:
        print(f" MongoDB Atlas connection failed: {str(e)}")
        print("\n Troubleshooting tips:")
        print("1. Check your MongoDB Atlas URI is correct")
        print("2. Ensure your IP address is whitelisted in Atlas")
        print("3. Verify your username and password")
        print("4. Make sure your cluster is active")
        return
    
    print("\n Setup complete!")
    print("\n Starting the application...")
    print("The app will open in your browser automatically.")
    print("\nPress Ctrl+C to stop the application.")
    
    # Run Streamlit
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    setup_and_run()