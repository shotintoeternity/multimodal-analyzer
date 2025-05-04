import os
import base64
import httpx
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import logging
from io import BytesIO
from PIL import Image

# Load environment variables
load_dotenv()

class GroqClient:
    """Client for interacting with Groq's API for vision and language processing"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
        
        if not self.api_key:
            logging.warning("GROQ_API_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_image(self, image_data: bytes, extracted_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image using Groq's vision API
        
        Args:
            image_data: Raw image bytes
            extracted_text: Any text extracted from the image via OCR
            
        Returns:
            Analysis results from Groq
        """
        try:
            # Convert image to base64
            base64_image = self._encode_image(image_data)
            
            # Prepare the prompt based on the type of technical image
            prompt = """
            Analyze this technical image in detail. If it's a diagram, describe its components and relationships.
            If it's a screenshot, identify UI elements, error messages, or notable features.
            If it contains code or terminal output, extract and explain key information.
            Identify any potential issues or errors visible in the image.
            """
            
            # Add extracted text to the prompt if available
            if extracted_text:
                prompt += f"\n\nText extracted from the image: {extracted_text}"
            
            # Prepare the request payload for Groq's vision API
            payload = {
                "model": "llama3-70b-8192-vision",  # Use appropriate Groq vision model
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1024
            }
            
            # Make the API call
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logging.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {"error": f"API error: {response.status_code}", "details": response.text}
                
                result = response.json()
                
                # Process and structure the response
                analysis = {
                    "description": result["choices"][0]["message"]["content"],
                    "detected_elements": self._extract_elements(result["choices"][0]["message"]["content"]),
                    "potential_issues": self._extract_issues(result["choices"][0]["message"]["content"])
                }
                
                return analysis
                
        except Exception as e:
            logging.error(f"Error in analyze_image: {str(e)}")
            raise
    
    async def analyze_code(self, code_content: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using Groq's language models
        
        Args:
            code_content: The code to analyze
            language: Detected programming language
            
        Returns:
            Analysis results from Groq
        """
        try:
            # Prepare the prompt
            prompt = f"""
            Analyze this {language} code:
            ```{language}
            {code_content}
            ```
            
            Provide a detailed analysis including:
            1. Code structure and organization
            2. Potential bugs or errors
            3. Performance issues
            4. Security concerns
            5. Best practices violations
            6. Suggestions for improvement
            """
            
            # Prepare the request payload
            payload = {
                "model": "llama3-70b-8192",  # Use appropriate Groq model
                "messages": [
                    {"role": "system", "content": "You are an expert code analyzer specializing in identifying issues and providing solutions."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2048
            }
            
            # Make the API call
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logging.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {"error": f"API error: {response.status_code}", "details": response.text}
                
                result = response.json()
                
                # Process and structure the response
                analysis_text = result["choices"][0]["message"]["content"]
                
                analysis = {
                    "language": language,
                    "summary": self._extract_summary(analysis_text),
                    "issues": self._extract_code_issues(analysis_text),
                    "suggestions": self._extract_suggestions(analysis_text),
                    "full_analysis": analysis_text
                }
                
                return analysis
                
        except Exception as e:
            logging.error(f"Error in analyze_code: {str(e)}")
            raise
    
    async def analyze_combined(
        self, 
        image_data: bytes, 
        extracted_text: str,
        code_content: str,
        language: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform combined analysis of image and code
        
        Args:
            image_data: Raw image bytes
            extracted_text: Text extracted from the image
            code_content: The code to analyze
            language: Detected programming language
            context: Additional context provided by the user
            
        Returns:
            Combined analysis results
        """
        try:
            # Convert image to base64
            base64_image = self._encode_image(image_data)
            
            # Prepare the prompt
            prompt = """
            Analyze both the provided image and code together to identify issues and provide solutions.
            
            For the image: Identify any error messages, UI issues, or relevant visual information.
            
            For the code: Analyze structure, potential bugs, and how it might relate to what's shown in the image.
            
            Provide a comprehensive analysis that connects the visual information with the code.
            """
            
            if context:
                prompt += f"\n\nAdditional context from the user: {context}"
            
            # Prepare the request payload for Groq's vision API
            payload = {
                "model": "llama3-70b-8192-vision",  # Use appropriate Groq vision model
                "messages": [
                    {"role": "system", "content": "You are an expert technical troubleshooter specializing in analyzing both visual information and code to solve problems."},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": f"Code ({language}):\n```{language}\n{code_content}\n```"
                            }
                        ]
                    }
                ],
                "max_tokens": 2048
            }
            
            # Make the API call
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logging.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {"error": f"API error: {response.status_code}", "details": response.text}
                
                result = response.json()
                
                # Process and structure the response
                analysis_text = result["choices"][0]["message"]["content"]
                
                analysis = {
                    "combined_analysis": analysis_text,
                    "image_elements": self._extract_elements(analysis_text),
                    "code_issues": self._extract_code_issues(analysis_text),
                    "correlations": self._extract_correlations(analysis_text),
                    "root_causes": self._extract_root_causes(analysis_text)
                }
                
                return analysis
                
        except Exception as e:
            logging.error(f"Error in analyze_combined: {str(e)}")
            raise
    
    def generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on analysis results
        
        Args:
            analysis_result: The analysis results from Groq
            
        Returns:
            List of recommendations
        """
        # Extract recommendations based on the type of analysis
        recommendations = []
        
        if "issues" in analysis_result:
            # Code analysis recommendations
            for issue in analysis_result["issues"]:
                if isinstance(issue, dict) and "solution" in issue:
                    recommendations.append(issue["solution"])
                elif isinstance(issue, str):
                    recommendations.append(f"Fix the issue: {issue}")
        
        if "potential_issues" in analysis_result:
            # Image analysis recommendations
            for issue in analysis_result["potential_issues"]:
                recommendations.append(f"Address the issue: {issue}")
        
        if "root_causes" in analysis_result:
            # Combined analysis recommendations
            for cause in analysis_result["root_causes"]:
                recommendations.append(f"Resolve root cause: {cause}")
        
        if "suggestions" in analysis_result:
            # Add any explicit suggestions
            recommendations.extend(analysis_result["suggestions"])
        
        # If no structured recommendations were found, extract from full text
        if not recommendations and "full_analysis" in analysis_result:
            recommendations = self._extract_suggestions(analysis_result["full_analysis"])
        
        # If still no recommendations, add a generic one
        if not recommendations and "combined_analysis" in analysis_result:
            recommendations = self._extract_suggestions(analysis_result["combined_analysis"])
        
        # Fallback
        if not recommendations:
            recommendations = ["Review the full analysis for detailed recommendations"]
        
        return recommendations
    
    def _encode_image(self, image_data: bytes) -> str:
        """Convert image bytes to base64 encoding"""
        # Ensure the image is in a supported format and resize if needed
        try:
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed (e.g., for PNG with transparency)
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize if the image is too large
            max_size = 1024  # Max dimension
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            processed_image_data = buffer.getvalue()
            
            # Encode to base64
            return base64.b64encode(processed_image_data).decode("utf-8")
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            # Fall back to direct encoding if image processing fails
            return base64.b64encode(image_data).decode("utf-8")
    
    def _extract_elements(self, text: str) -> List[str]:
        """Extract key elements from analysis text"""
        elements = []
        
        # Look for lists or key elements in the text
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if (":" in line and not line.endswith(":")) or \
               (line.strip().startswith("-") or line.strip().startswith("*")) or \
               (line.strip().startswith(str(len(elements) + 1) + ".")) or \
               ("component" in line.lower() or "element" in line.lower()):
                elements.append(line.strip())
        
        # Limit to reasonable number
        return elements[:10] if elements else ["No specific elements identified"]
    
    def _extract_issues(self, text: str) -> List[str]:
        """Extract potential issues from analysis text"""
        issues = []
        
        # Look for mentions of issues, errors, problems
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ["error", "issue", "problem", "bug", "warning", "fail"]):
                issues.append(line.strip())
        
        # Limit to reasonable number
        return issues[:5] if issues else ["No specific issues identified"]
    
    def _extract_code_issues(self, text: str) -> List[Dict[str, str]]:
        """Extract code issues with more structure"""
        issues = []
        
        # Look for sections about issues
        sections = text.split("\n\n")
        current_issue = None
        
        for section in sections:
            if any(keyword in section.lower() for keyword in ["issue", "bug", "error", "problem"]):
                lines = section.split("\n")
                if len(lines) >= 2:
                    issue = {
                        "description": lines[0].strip(),
                        "details": "\n".join(lines[1:]).strip()
                    }
                    
                    # Look for solution in nearby text
                    solution_idx = text.find("solution", text.find(section))
                    if solution_idx != -1:
                        end_idx = text.find("\n\n", solution_idx)
                        if end_idx != -1:
                            issue["solution"] = text[solution_idx:end_idx].strip()
                    
                    issues.append(issue)
        
        # If structured approach didn't work, fall back to simpler extraction
        if not issues:
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in ["issue", "bug", "error", "problem"]):
                    issues.append({"description": line.strip()})
        
        return issues[:5] if issues else [{"description": "No specific issues identified"}]
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggestions from analysis text"""
        suggestions = []
        
        # Look for suggestions, recommendations, improvements
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ["suggest", "recommend", "improv", "should", "could", "better"]):
                suggestions.append(line.strip())
        
        # Limit to reasonable number
        return suggestions[:5] if suggestions else ["No specific suggestions identified"]
    
    def _extract_summary(self, text: str) -> str:
        """Extract a summary from the analysis"""
        # Look for initial paragraph or summary section
        paragraphs = text.split("\n\n")
        
        for para in paragraphs:
            if len(para.strip()) > 50 and "summary" in para.lower():
                return para.strip()
        
        # If no explicit summary, use first paragraph
        if paragraphs and len(paragraphs[0].strip()) > 30:
            return paragraphs[0].strip()
        
        return "No summary available"
    
    def _extract_correlations(self, text: str) -> List[str]:
        """Extract correlations between image and code"""
        correlations = []
        
        # Look for sentences that mention both visual and code elements
        sentences = text.replace("\n", " ").split(". ")
        for sentence in sentences:
            if (("image" in sentence.lower() or "screen" in sentence.lower() or "visual" in sentence.lower()) and 
                ("code" in sentence.lower() or "function" in sentence.lower() or "variable" in sentence.lower())):
                correlations.append(sentence.strip() + ".")
        
        return correlations[:3] if correlations else ["No specific correlations identified"]
    
    def _extract_root_causes(self, text: str) -> List[str]:
        """Extract potential root causes of issues"""
        causes = []
        
        # Look for root cause language
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(phrase in line.lower() for phrase in ["root cause", "caused by", "due to", "because", "reason for"]):
                causes.append(line.strip())
        
        return causes[:3] if causes else ["Root cause not specifically identified"]
