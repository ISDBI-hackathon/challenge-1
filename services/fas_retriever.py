from typing import Dict, Any, List
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from tenacity import retry, stop_after_attempt, wait_exponential


class FASRetriever:
    def __init__(self, embeddings_dir: str = "embeddings"):
        api_key = "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"
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small",  # Using the newer, more efficient model
        )
        self.embeddings_dir = Path(embeddings_dir)
        self.embeddings_dir.mkdir(exist_ok=True)
        self.fas_docs = {}

    def _get_embedding_path(self, fas_number: str) -> Path:
        """Get the path for storing embeddings for a specific FAS"""
        return self.embeddings_dir / f"fas_{fas_number}"

    def save_embeddings(self, fas_number: str):
        """Save the FAISS vector store for a specific FAS"""
        if fas_number not in self.fas_docs:
            return

        embedding_path = self._get_embedding_path(fas_number)
        self.fas_docs[fas_number].save_local(str(embedding_path))

    def load_embeddings(self, fas_number: str) -> bool:
        """Load the FAISS vector store for a specific FAS if it exists"""
        embedding_path = self._get_embedding_path(fas_number)
        if embedding_path.exists():
            try:
                self.fas_docs[fas_number] = FAISS.load_local(
                    str(embedding_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True,  # Safe since we generated these embeddings ourselves
                )
                return True
            except Exception as e:
                print(f"Error loading embeddings for FAS {fas_number}: {str(e)}")
        return False

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def load_fas_documents(self, fas_docs_dir: str):
        """
        Load and process FAS PDF documents with retry logic for rate limits.
        Only processes documents that don't have existing embeddings.
        """
        docs_dir = Path(fas_docs_dir)
        if not docs_dir.exists():
            raise ValueError(f"FAS documents directory not found: {fas_docs_dir}")

        # Load each FAS document
        for pdf_file in docs_dir.glob("*.pdf"):
            try:
                fas_number = pdf_file.stem.split("_")[
                    0
                ]  # Assuming filename format: "FAS4_Description.pdf"

                # Try to load existing embeddings first
                if self.load_embeddings(fas_number):
                    print(f"Loaded existing embeddings for FAS {fas_number}")
                    continue

                print(f"Processing new document for FAS {fas_number}")
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()

                # Split documents into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, chunk_overlap=200
                )
                chunks = text_splitter.split_documents(pages)

                # Create vector store for this FAS
                self.fas_docs[fas_number] = FAISS.from_documents(
                    chunks, self.embeddings
                )

                # Save the embeddings
                self.save_embeddings(fas_number)

            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
                continue

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_relevant_context(self, fas_standard: str, query: str) -> str:
        """
        Retrieve relevant context from the specified FAS standard with retry logic
        """
        if fas_standard not in self.fas_docs:
            raise ValueError(
                f"FAS standard {fas_standard} not found in loaded documents"
            )

        try:
            # Search for relevant chunks
            docs = self.fas_docs[fas_standard].similarity_search(query, k=3)

            # Combine relevant context
            context = "\n\n".join([doc.page_content for doc in docs])
            return context
        except Exception as e:
            print(f"Error retrieving context for {fas_standard}: {str(e)}")
            return ""
