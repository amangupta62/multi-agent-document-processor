import pdfplumber
from typing import Dict, Any, Optional
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json

class ExtractorAgent:
    def __init__(self):
        self.name = "Extractor Agent"
    
    def process(self, pdf_path: str) -> str:
        """Extract text from PDF document."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

class SummarizerAgent:
    def __init__(self):
        self.name = "Summarizer Agent"
        self.llm = Ollama(model="llama3")
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""Please provide a concise summary of the following text. 
            Focus on the main points and key information:
            
            {text}
            
            Summary:"""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def process(self, text: str) -> str:
        """Generate a summary of the extracted text."""
        try:
            return self.chain.run(text=text)
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

class FieldExtractorAgent:
    def __init__(self):
        self.name = "Field Extractor Agent"
        self.llm = Ollama(model="llama3")
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""Analyze the following text and extract key fields in JSON format.
            Include fields like date, name, topic, and any other relevant information.
            Return only the JSON object without any additional text:
            
            {text}
            
            JSON:"""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def process(self, text: str) -> Dict[str, Any]:
        """Extract key fields from the text and return as structured JSON."""
        try:
            result = self.chain.run(text=text)
            # Clean the result to ensure it's valid JSON
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            return json.loads(result)
        except Exception as e:
            raise Exception(f"Error extracting fields: {str(e)}")

class DocumentProcessor:
    def __init__(self):
        self.extractor = ExtractorAgent()
        self.summarizer = SummarizerAgent()
        self.field_extractor = FieldExtractorAgent()
    
    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """Process document through all agents and return results."""
        try:
            # Extract text
            extracted_text = self.extractor.process(pdf_path)
            
            # Generate summary
            summary = self.summarizer.process(extracted_text)
            
            # Extract fields
            fields = self.field_extractor.process(extracted_text)
            
            return {
                "extracted_text": extracted_text,
                "summary": summary,
                "fields": fields
            }
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}") 