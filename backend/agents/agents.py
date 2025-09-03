from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ComplaintTools:
    def __init__(self, api_base_url="http://localhost:8001"):
        self.api_base_url = api_base_url
    
    def register_complaint(self, input_str: str) -> str:
        """Register a new complaint with flexible input parsing"""
        try:
            # Parse input
            name = ""
            mobile = ""
            complaint_details = ""
            
            # Try JSON parsing first
            try:
                if input_str.startswith('{'):
                    data = json.loads(input_str)
                    name = data.get('name', '')
                    mobile = data.get('mobile', '')
                    complaint_details = data.get('complaint_details', '')
                else:
                    # Parse comma-separated or other formats
                    parts = input_str.split(',')
                    if len(parts) >= 3:
                        name = parts[0].strip()
                        mobile = parts[1].strip()
                        complaint_details = ','.join(parts[2:]).strip()
            except:
                # Fallback parsing
                lines = input_str.strip().split('\n')
                for line in lines:
                    if 'name:' in line.lower():
                        name = line.split(':', 1)[1].strip()
                    elif 'mobile:' in line.lower() or 'phone:' in line.lower():
                        mobile = line.split(':', 1)[1].strip()
                    elif 'complaint:' in line.lower() or 'details:' in line.lower():
                        complaint_details = line.split(':', 1)[1].strip()
            
            # Validate
            if not all([name, mobile, complaint_details]):
                return "Please provide all required information: name, mobile number, and complaint details."
            
            # Make API call
            response = requests.post(
                f"{self.api_base_url}/api/register_complaint",
                json={
                    "name": name,
                    "mobile": mobile,
                    "complaint_details": complaint_details
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return f" {data['message']}"
            else:
                return f" Failed to register complaint: {response.text}"
                
        except Exception as e:
            return f" Error: {str(e)}"

    def check_complaint_status(self, complaint_id: str) -> str:
        """Check the status of a complaint"""
        try:
            complaint_id = complaint_id.strip()
            response = requests.get(
                f"{self.api_base_url}/api/complaint_status/{complaint_id}"
            )
            if response.status_code == 200:
                data = response.json()
                return f""" Complaint Status:
- ID: {data['complaint_id']}
- Status: {data['status']}
- Created: {data['created_at']}
- Updated: {data['updated_at']}"""
            else:
                return f" No complaint found with ID: {complaint_id}"
        except Exception as e:
            return f" Error: {str(e)}"
    
    def get_complaints_by_mobile(self, mobile: str) -> str:
        """Get all complaints for a mobile number"""
        try:
            mobile = mobile.strip()
            response = requests.get(
                f"{self.api_base_url}/api/complaints_by_mobile/{mobile}"
            )
            if response.status_code == 200:
                complaints = response.json()
                if complaints:
                    result = f"📱 Complaints for mobile {mobile}:\n\n"
                    for complaint in complaints:
                        result += f"• ID: {complaint['complaint_id']}\n"
                        result += f"  Status: {complaint['status']}\n"
                        result += f"  Details: {complaint['details']}\n"
                        result += f"  Created: {complaint['created_at']}\n\n"
                    return result
                else:
                    return f"No complaints found for mobile number: {mobile}"
            else:
                return f" Error fetching complaints"
        except Exception as e:
            return f" Error: {str(e)}"

def create_agent():
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.6,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize tools
    complaint_tools = ComplaintTools()
    
    tools = [
        Tool(
            name="register_complaint",
            func=complaint_tools.register_complaint,
            description="Register a new complaint. Input format: 'name, mobile, complaint details' or JSON"
        ),
        Tool(
            name="check_complaint_status",
            func=complaint_tools.check_complaint_status,
            description="Check complaint status. Input: complaint ID only"
        ),
        Tool(
            name="get_complaints_by_mobile",
            func=complaint_tools.get_complaints_by_mobile,
            description="Get all complaints for a mobile number. Input: mobile number only"
        )
    ]
    
    # Create a simpler prompt
    system_message = """You are a helpful customer service assistant for handling complaints.

When a user wants to register a complaint:
1. Ask for their name, mobile number, and complaint details
2. Once you have all information, use the register_complaint tool
3. Format: "Name, Mobile, Complaint Details"

When checking status:
- Ask for complaint ID and use check_complaint_status tool

When viewing all complaints:
- Ask for mobile number and use get_complaints_by_mobile tool

Be polite and helpful."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return agent_executor