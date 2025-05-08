from typing import Dict, Any, List
import openai
import os
import json
from .nlp_processor import ExtractedData
from .fas_retriever import FASRetriever
from tenacity import retry, stop_after_attempt, wait_exponential


class AccountingProcessor:
    def __init__(self, fas_docs_dir: str, embeddings_dir: str = "embeddings"):
        self.client = openai.OpenAI(
            api_key="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"
        )
        self.fas_retriever = FASRetriever(embeddings_dir=embeddings_dir)
        self.fas_retriever.load_fas_documents(fas_docs_dir)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_entries(
        self, data: ExtractedData, fas_standard: str
    ) -> Dict[str, Any]:
        """
        Generate AAOIFI-compliant accounting entries based on the extracted data
        """
        try:
            # Get relevant context from FAS documents
            query = f"""
            Transaction Type: {data.transaction_type}
            Amounts: {data.amounts}
            Terms: {data.terms}
            """
            fas_context = self.fas_retriever.get_relevant_context(fas_standard, query)

            prompt = f"""
            Generate AAOIFI-compliant accounting entries for the following transaction data.
            Use the provided FAS standard context to ensure compliance:

            FAS Standard Context:
            {fas_context}

            Transaction Data:
            Transaction Type: {data.transaction_type}
            FAS Standard: {fas_standard}
            
            Parties:
            {data.parties}
            
            Amounts:
            {data.amounts}
            
            Dates:
            {data.dates}
            
            Terms:
            {data.terms}
            
            Additional Info:
            {data.additional_info}
            
            Return ONLY a JSON object with the following structure, no markdown formatting or additional text:
            {{
                "journal_entries": [
                    {{
                        "date": "",
                        "description": "",
                        "entries": [
                            {{"account": "", "debit": amount, "credit": amount}}
                        ]
                    }}
                ],
                "calculations": {{
                    "calculation_name": "value"
                }},
                "explanation": "",
                "fas_references": [
                    {{
                        "section": "",
                        "relevance": ""
                    }}
                ]
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in AAOIFI accounting standards. Generate compliant accounting entries based on the provided FAS standard context. Return only valid JSON, no markdown or additional text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            try:
                # Get the response content and parse it as JSON
                content = response.choices[0].message.content
                # Remove any markdown formatting if present
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {content}")
                raise ValueError(f"Failed to parse accounting response: {str(e)}")

        except Exception as e:
            print(f"Error generating entries: {str(e)}")
            raise
