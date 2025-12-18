from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys
import logging
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from main import create_workflow_instance

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="GitHub Issue Creator API",
    description="AI-powered GitHub issue creation workflow",
    version="1.0.0"
)

class IssueRequest(BaseModel):
    description: str
    issue_type: Optional[str] = "bug"
    stack_trace: Optional[str] = None

class IssueResponse(BaseModel):
    status: str
    result: dict
    message: str

@app.post("/api/issues/create", response_model=IssueResponse)
async def create_issue(request: IssueRequest):
    """Create a GitHub issue using AI workflow"""
    try:
        logging.info(f"Received request: {request.description}")
        
        workflow, _, _, _, _ = create_workflow_instance()
        
        input_text = request.description
        if request.stack_trace:
            input_text += f"\n\nStack Trace:\n{request.stack_trace}"
        
        # Fix: Pass input as positional argument, not keyword
        result = await workflow.run(input_text)
        
        return IssueResponse(
            status="success",
            result=result if isinstance(result, dict) else {"output": str(result)},
            message="Issue created successfully"
        )
    except Exception as e:
        logging.error(f"Error creating issue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "github-issue-creator"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GitHub Issue Creator API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }