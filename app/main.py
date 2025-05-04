from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import os
import uuid
import json
from datetime import datetime, timedelta

from app.utils.groq_client import GroqClient
from app.utils.image_processor import ImageProcessor
from app.utils.code_analyzer import CodeAnalyzer

app = FastAPI(title="Multimodal Technical Analysis System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize components
groq_client = GroqClient()
image_processor = ImageProcessor()
code_analyzer = CodeAnalyzer()

class AnalysisRequest(BaseModel):
    analysis_type: str  # "image", "code", or "combined"
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    result: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Multimodal Technical Analysis System</title>
            <link rel="stylesheet" href="/static/styles.css">
        </head>
        <body>
            <h1>Multimodal Technical Analysis System</h1>
            <p>API is running. Use the endpoints to analyze technical content.</p>
            <script src="/static/script.js"></script>
        </body>
    </html>
    """

@app.post("/api/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze a technical diagram or screenshot using Groq's vision API
    """
    try:
        # Process the image
        image_data = await file.read()
        processed_image = image_processor.preprocess(image_data)
        
        # Extract text if present
        extracted_text = image_processor.extract_text(processed_image)
        
        # Send to Groq for analysis
        analysis_result = await groq_client.analyze_image(processed_image, extracted_text)
        
        # Generate recommendations
        recommendations = groq_client.generate_recommendations(analysis_result)
        
        return AnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            result=analysis_result,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.post("/api/analyze/code", response_model=AnalysisResponse)
async def analyze_code(code_file: UploadFile = File(...)):
    """
    Analyze code snippets for issues and provide troubleshooting
    """
    try:
        # Read and process the code
        code_content = await code_file.read()
        code_content = code_content.decode("utf-8")
        
        # Detect language and parse code
        language = code_analyzer.detect_language(code_content)
        parsed_code = code_analyzer.parse_code(code_content, language)
        
        # Send to Groq for analysis
        analysis_result = await groq_client.analyze_code(parsed_code, language)
        
        # Generate recommendations
        recommendations = groq_client.generate_recommendations(analysis_result)
        
        return AnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            result=analysis_result,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")

@app.post("/api/analyze/combined", response_model=AnalysisResponse)
async def analyze_combined(
    image_file: UploadFile = File(...),
    code_file: UploadFile = File(...),
    context: str = Form(None)
):
    """
    Analyze both image and code together for comprehensive troubleshooting
    """
    try:
        # Process image
        image_data = await image_file.read()
        processed_image = image_processor.preprocess(image_data)
        extracted_text = image_processor.extract_text(processed_image)
        
        # Process code
        code_content = await code_file.read()
        code_content = code_content.decode("utf-8")
        language = code_analyzer.detect_language(code_content)
        parsed_code = code_analyzer.parse_code(code_content, language)
        
        # Send to Groq for combined analysis
        analysis_result = await groq_client.analyze_combined(
            processed_image, 
            extracted_text,
            parsed_code,
            language,
            context
        )
        
        # Generate recommendations
        recommendations = groq_client.generate_recommendations(analysis_result)
        
        return AnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            result=analysis_result,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combined analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
