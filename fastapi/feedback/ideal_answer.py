import os
from groq import Groq
from typing import Dict, Optional
from fastapi import HTTPException
import unicodedata
import json
import logging

# Configure logging to output detailed info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdealAnswerGenerator:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    @staticmethod
    def parse_llm_response(response: str) -> Dict:
        """Parse and validate LLM response with unicode support."""
        logger.info("Attempting to parse LLM response...")
        # Normalize unicode characters
        normalized_response = unicodedata.normalize('NFKC', response)
    
        # Remove markdown code fences
        if normalized_response.strip().startswith('```'):
            # Remove opening fence and optional language identifier
            normalized_response = normalized_response.strip()
            normalized_response = normalized_response.lstrip('`').lstrip('json').lstrip('`').strip()
            # Remove closing fence
            normalized_response = normalized_response.rstrip('`').strip()
    
        try:
            # Parse JSON
            parsed = json.loads(normalized_response)
        
            # Validate required fields exactly as requested in the prompt
            required_fields = [
                'ideal_answer', 
                'user_strengths', 
                'areas_for_improvement', 
                'improvement_suggestions'
            ]
        
            missing_fields = [field for field in required_fields if field not in parsed]
            if missing_fields:
                logger.error(f"Validation failed. Missing fields: {missing_fields}")
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
                
            logger.info("Response successfully parsed and validated.")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)} | Raw Response: {response}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse LLM response as JSON: {str(e)}"
            )
        except ValueError as e:
            logger.error(f"Value Error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def generate_ideal_answer(self, question: str, user_answer: str) -> Dict:
        """
        Generate a grammatically correct answer and analysis.
        """
        try:
            logger.info(f"Generating ideal answer for question: {question[:50]}...")
            
            # Prompt aligned with parser requirements
            prompt = f"""
            Question: {question}
            User's Answer: {user_answer}
            
            Please provide:
            1. A corrected grammatical answer to this question
            2. Analysis of what the user did well
            3. Areas where the user's answer could be improved
            4. Specific suggestions for further improvement
            
            Format the response ONLY as a JSON object with this exact structure:
            {{
                "ideal_answer": "corrected answer",
                "user_strengths": "strengths analysis",
                "areas_for_improvement": "weakness analysis",
                "improvement_suggestions": "actionable tips"
            }}
            """

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a grammatical assessment expert. You output ONLY valid JSON.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.1,
                model=self.model,
            )            
    
            response_text = chat_completion.choices[0].message.content
            logger.info(f"Raw LLM output received: {response_text}")

            # Correctly call the static method to parse the string into a Dict
            parsed_data = IdealAnswerGenerator.parse_llm_response(response_text)
            logger.info(f"Parsed data: {parsed_data}") 
            return {
                "status": "success",
                "data": parsed_data
            }

        except Exception as e:
            logger.error(f"Failed to generate ideal answer: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Ideal Answer Generator Error: {str(e)}"
            )

# Create a singleton instance
# ideal_answer_generator = IdealAnswerGenerator()