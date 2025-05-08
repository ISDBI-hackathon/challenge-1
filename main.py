from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from services.accounting_processor import AccountingProcessor
from services.nlp_processor import NLPProcessor

load_dotenv()

app = FastAPI(
    title="AAOIFI Accounting Entry Generator",
    description="AI agent that generates AAOIFI-compliant accounting entries from natural language input",
)

# Initialize processors
fas_docs_dir = "fas_documents"
embeddings_dir = "embeddings"
accounting_processor = AccountingProcessor(fas_docs_dir, embeddings_dir)
nlp_processor = NLPProcessor()


class AccountingRequest(BaseModel):
    input_text: str
    fas_standard: str  # FAS 4, 7, 10, 28, or 32


class AccountingResponse(BaseModel):
    journal_entries: List[Dict[str, Any]]
    calculations: Dict[str, Any]
    explanation: str
    fas_references: List[Dict[str, str]]


@app.post("/generate-entries", response_model=AccountingResponse)
async def generate_accounting_entries(request: AccountingRequest):
    try:
        # Process the input text
        extracted_data = nlp_processor.process_input(request.input_text)

        # Generate accounting entries
        result = accounting_processor.generate_entries(
            extracted_data, request.fas_standard
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
