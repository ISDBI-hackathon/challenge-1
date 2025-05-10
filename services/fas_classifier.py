from typing import Dict, List, Any
import openai
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

class FASStandard(Enum):
    FAS4 = "Musharaka"
    FAS7 = "Salam"
    FAS10 = "Istisna"
    FAS28 = "Murabaha"
    FAS32 = "Ijarah"

@dataclass
class FASWeight:
    standard: FASStandard
    weight: float
    confidence: float
    relevance_explanation: str
    relevant_sections: List[str]  # Added to store relevant sections from FAS documents

class FASClassifier:
    def __init__(self, fas_docs_dir: str = "fas_documents"):
        self.client = openai.OpenAI(api_key="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")
        self.embeddings = OpenAIEmbeddings(
            openai_api_key="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",
            model="text-embedding-3-small"
        )
        self.fas_docs = {}
        self.load_fas_documents(fas_docs_dir)
        
    def load_fas_documents(self, fas_docs_dir: str):
        """
        Load and process FAS PDF documents
        """
        docs_dir = Path(fas_docs_dir)
        if not docs_dir.exists():
            raise ValueError(f"FAS documents directory not found: {fas_docs_dir}")
            
        # Load each FAS document
        for pdf_file in docs_dir.glob("FAS*.pdf"):
            try:
                # Extract FAS number from filename (e.g., "FAS4_Musharaka.pdf" -> "FAS4")
                fas_number = pdf_file.stem.split("_")[0]
                if not fas_number.startswith("FAS"):
                    continue
                    
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()
                
                # Split documents into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_documents(pages)
                
                # Create vector store for this FAS
                self.fas_docs[fas_number] = FAISS.from_documents(chunks, self.embeddings)
                print(f"Loaded {fas_number} with {len(chunks)} chunks")
                
            except Exception as e:
                print(f"Error loading {pdf_file}: {str(e)}")
                continue
        
    def get_relevant_sections(self, fas_standard: str, query: str, k: int = 3) -> List[str]:
        """
        Get relevant sections from a specific FAS standard
        """
        if fas_standard not in self.fas_docs:
            return []
            
        docs = self.fas_docs[fas_standard].similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
        
    def classify_transaction(self, transaction_text: str) -> List[FASWeight]:
        """
        Analyze a transaction and return weighted FAS standards with confidence scores
        """
        # First, get relevant sections from all FAS documents
        fas_contexts = {}
        for fas in FASStandard:
            fas_number = fas.name
            relevant_sections = self.get_relevant_sections(fas_number, transaction_text)
            if relevant_sections:
                fas_contexts[fas_number] = "\n\n".join(relevant_sections)
        
        prompt = f"""
        Analyze the following Islamic finance transaction and determine which AAOIFI FAS standards are applicable.
        For each applicable standard, provide:
        1. A weight (0-1) indicating how relevant it is
        2. A confidence score (0-1) in your assessment
        3. A brief explanation of why it's relevant
        4. Reference to specific sections from the FAS documents

        Transaction:
        {transaction_text}

        Relevant FAS Sections:
        {json.dumps(fas_contexts, indent=2)}

        Return ONLY a JSON array of objects with the following structure:
        [
            {{
                "standard": "FAS number (e.g., FAS4)",
                "weight": float between 0 and 1,
                "confidence": float between 0 and 1,
                "relevance_explanation": "Brief explanation",
                "relevant_sections": ["section1", "section2"]
            }}
        ]

        Consider these standards:
        - FAS 4: Musharaka
        - FAS 7: Salam
        - FAS 10: Istisna
        - FAS 28: Murabaha
        - FAS 32: Ijarah
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert in Islamic finance and AAOIFI standards. Analyze transactions and identify applicable FAS standards with weights and confidence scores. Use the provided FAS sections to support your analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        
        try:
            content = response.choices[0].message.content
            content = content.replace('```json', '').replace('```', '').strip()
            weights_data = json.loads(content)
            
            # Convert to FASWeight objects
            fas_weights = []
            for weight_data in weights_data:
                standard = FASStandard[weight_data['standard'].replace(' ', '')]
                fas_weights.append(FASWeight(
                    standard=standard,
                    weight=float(weight_data['weight']),
                    confidence=float(weight_data['confidence']),
                    relevance_explanation=weight_data['relevance_explanation'],
                    relevant_sections=weight_data.get('relevant_sections', [])
                ))
            
            # Sort by weight (highest first)
            return sorted(fas_weights, key=lambda x: x.weight, reverse=True)
            
        except Exception as e:
            print(f"Error in FAS classification: {str(e)}")
            raise

    def get_primary_standard(self, transaction_text: str) -> FASWeight:
        """
        Get the most relevant FAS standard for a transaction
        """
        weights = self.classify_transaction(transaction_text)
        return weights[0] if weights else None

    def get_standards_above_threshold(self, transaction_text: str, threshold: float = 0.3) -> List[FASWeight]:
        """
        Get all FAS standards with weights above a certain threshold
        """
        weights = self.classify_transaction(transaction_text)
        return [w for w in weights if w.weight >= threshold] 