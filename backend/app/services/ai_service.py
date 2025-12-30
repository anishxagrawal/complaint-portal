# app/services/ai_service.py
import os
import json
from typing import Dict, Optional
import google.generativeai as genai
from fastapi import HTTPException
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

class AIService:
    """
    Service for AI-powered complaint extraction.
    Uses Google Gemini to extract structured data from natural language.
    """
    
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            # Print debug info
            print("❌ GEMINI_API_KEY not found in environment variables")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Looking for .env file...")
            
            # Try to find .env file
            env_locations = [
                ".env",
                "../.env",
                "backend/.env",
                os.path.join(os.getcwd(), ".env")
            ]
            
            for loc in env_locations:
                if os.path.exists(loc):
                    print(f"✅ Found .env at: {loc}")
                    load_dotenv(loc, override=True)
                    self.api_key = os.getenv("GEMINI_API_KEY")
                    if self.api_key:
                        print("✅ GEMINI_API_KEY loaded successfully")
                        break
            
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY environment variable not set. "
                    "Please add it to your .env file. "
                    "Get your free API key from: https://aistudio.google.com/app/apikey"
                )
        
        # Configure Gemini
        try:
            genai.configure(api_key=self.api_key)
            # Use the correct model name for free tier
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI Service initialized successfully")
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {str(e)}")
    
    def extract_complaint_info(self, user_message: str) -> Dict:
        """
        Extract complaint information from natural language.
        
        Args:
            user_message: User's complaint in natural language
            
        Returns:
            {
                "description": str,
                "address": str,
                "issue_type": str,
                "urgency": str,
                "confidence": float,
                "needs_clarification": bool,
                "clarification_questions": List[str]
            }
        """
        
        prompt = f"""You are a complaint processing assistant for a municipal complaint system.

Extract the following information from the user's complaint:

1. **Description**: A clear summary of the issue
2. **Address/Location**: Where the problem is (street name, area, landmark)
3. **Issue Type**: Categorize as one of:
   - Roads (potholes, damaged roads)
   - Water Supply (leaks, no water, contamination)
   - Electricity (power outage, streetlights)
   - Sanitation (garbage, drainage, cleanliness)
   - Public Infrastructure (parks, buildings)
   - Other

4. **Urgency**: Rate as LOW, MEDIUM, HIGH, or CRITICAL
   - CRITICAL: Immediate danger (gas leak, major accident)
   - HIGH: Significant impact (no water, major pothole)
   - MEDIUM: Moderate inconvenience (streetlight out)
   - LOW: Minor issue (cosmetic damage)

5. **Confidence**: How confident are you (0.0-1.0)?

6. **Needs Clarification**: Does the complaint need more information?

User's complaint:
"{user_message}"

Respond ONLY with valid JSON in this exact format (no markdown, no backticks, just raw JSON):
{{
    "description": "string",
    "address": "string",
    "issue_type": "string",
    "urgency": "string",
    "confidence": 0.85,
    "needs_clarification": false,
    "clarification_questions": []
}}

If information is missing or unclear, set needs_clarification to true and list questions."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            extracted_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = [
                "description", "address", "issue_type", 
                "urgency", "confidence", "needs_clarification"
            ]
            
            for field in required_fields:
                if field not in extracted_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure clarification_questions exists
            if "clarification_questions" not in extracted_data:
                extracted_data["clarification_questions"] = []
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"Response text: {response_text[:200]}")
            
            # Return fallback structure
            return {
                "description": user_message[:100],
                "address": "Not specified",
                "issue_type": "Other",
                "urgency": "MEDIUM",
                "confidence": 0.3,
                "needs_clarification": True,
                "clarification_questions": [
                    "Where exactly is this issue located?",
                    "Can you provide more details about the problem?"
                ]
            }
        except Exception as e:
            print(f"❌ AI extraction error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"AI extraction failed: {str(e)}"
            )
    
    def generate_clarification_response(
        self, 
        original_message: str,
        extracted_info: Dict,
        user_response: str
    ) -> Dict:
        """
        Handle follow-up questions and clarifications.
        
        Returns updated extracted_info with new information.
        """
        
        prompt = f"""You previously extracted this information from a complaint:
{json.dumps(extracted_info, indent=2)}

Original complaint: "{original_message}"

User's clarification: "{user_response}"

Update the extracted information based on the clarification.
Respond ONLY with the updated JSON in the same format (no markdown, no backticks, just raw JSON):
{{
    "description": "string",
    "address": "string",
    "issue_type": "string",
    "urgency": "string",
    "confidence": 0.85,
    "needs_clarification": false,
    "clarification_questions": []
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            updated_data = json.loads(response_text)
            
            # Ensure clarification_questions exists
            if "clarification_questions" not in updated_data:
                updated_data["clarification_questions"] = []
            
            return updated_data
            
        except Exception as e:
            print(f"⚠️ Clarification update failed: {e}")
            return extracted_info

# Singleton instance
_ai_service_instance: Optional[AIService] = None

def get_ai_service() -> AIService:
    """
    Dependency injection for FastAPI.
    Creates singleton instance on first call.
    """
    global _ai_service_instance
    
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    
    return _ai_service_instance