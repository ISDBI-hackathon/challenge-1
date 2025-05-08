from typing import Dict, Any
import openai
from pydantic import BaseModel
import os
import json

class ExtractedData(BaseModel):
    transaction_type: str
    parties: Dict[str, str]
    amounts: Dict[str, float]
    dates: Dict[str, str]
    terms: Dict[str, Any]
    additional_info: Dict[str, Any]

class NLPProcessor:
    def __init__(self):
        self.client = openai.OpenAI(api_key="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")
        
    def process_input(self, input_text: str) -> ExtractedData:
        """
        Process natural language input to extract structured data
        """
        prompt = f"""
        Extract the following information from the accounting scenario:
        1. Transaction type (e.g., Ijarah, Murabaha, etc.)
        2. Parties involved and their roles
        3. All monetary amounts
        4. Important dates
        5. Terms and conditions
        6. Additional relevant information
        
        Scenario:
        {input_text}
        
        Return ONLY a JSON object with the following structure, no markdown formatting or additional text:
        {{
            "transaction_type": "",
            "parties": {{"role": "name"}},
            "amounts": {{"description": amount}},
            "dates": {{"event": "date"}},
            "terms": {{"term": "value"}},
            "additional_info": {{"info": "value"}}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert in Islamic finance and accounting. Extract structured data from accounting scenarios. Return only valid JSON, no markdown or additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        
        try:
            # Get the response content and parse it as JSON
            content = response.choices[0].message.content
            # Remove any markdown formatting if present
            content = content.replace('```json', '').replace('```', '').strip()
            data = json.loads(content)
            return ExtractedData(**data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {content}")
            raise ValueError(f"Failed to parse NLP response: {str(e)}")
        except Exception as e:
            print(f"Unexpected error in NLP processing: {e}")
            raise 