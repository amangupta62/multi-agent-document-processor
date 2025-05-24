import pdfplumber
from typing import Dict, Any, Optional
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
import json
import re
from logger_config import setup_logger

# Setup loggers for each agent
extractor_logger = setup_logger('extractor_agent')
summarizer_logger = setup_logger('summarizer_agent')
field_extractor_logger = setup_logger('field_extractor_agent')
processor_logger = setup_logger('document_processor')

class ExtractorAgent:
    def __init__(self):
        self.name = "Extractor Agent"
        self.logger = extractor_logger
    
    def process(self, pdf_path: str) -> str:
        """Extract text from PDF document."""
        self.logger.info(f"Starting text extraction from PDF: {pdf_path}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for i, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Processing page {i}")
                    page_text = page.extract_text() or ""
                    text += page_text
                self.logger.info(f"Successfully extracted text from {len(pdf.pages)} pages")
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
            raise Exception(f"Error extracting text from PDF: {str(e)}")

class SummarizerAgent:
    def __init__(self):
        self.name = "Summarizer Agent"
        self.logger = summarizer_logger
        self.llm = Ollama(model="llama3")
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""Please provide a concise summary of the following text. 
            Focus on the main points and key information:
            
            {text}
            
            Summary:"""
        )
        self.chain = self.prompt | self.llm
    
    def process(self, text: str) -> str:
        """Generate a summary of the extracted text."""
        self.logger.info("Starting text summarization")
        try:
            summary = self.chain.invoke({"text": text})
            self.logger.info("Successfully generated summary")
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            raise Exception(f"Error generating summary: {str(e)}")

class FieldExtractorAgent:
    def __init__(self):
        self.name = "Field Extractor Agent"
        self.logger = field_extractor_logger
        self.llm = Ollama(model="llama3")
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""Analyze the following text and extract key information into a JSON object.
            Include these fields if present in the text:
            - date: The date mentioned in the document
            - title: The title or main topic
            - author: The author or sender
            - recipient: The recipient or audience
            - main_points: A list of key points or topics
            - summary: A brief summary of the content
            
            Return ONLY a valid JSON object with no additional text or explanation.
            Example format:
            {{
                "date": "2024-03-20",
                "title": "Sample Document",
                "author": "John Doe",
                "recipient": "Jane Smith",
                "main_points": ["Point 1", "Point 2"],
                "summary": "Brief summary here"
            }}
            
            Text to analyze:
            {text}
            
            JSON:"""
        )
        self.chain = self.prompt | self.llm
    
    def process(self, text: str) -> Dict[str, Any]:
        """Extract key fields from the text and return as structured JSON."""
        self.logger.info("Starting field extraction")
        try:
            result = self.chain.invoke({"text": text})
            self.logger.debug("Received raw LLM response")
            
            # Clean the result to ensure it's valid JSON
            result = result.strip()
            
            # Remove any markdown code block markers
            result = re.sub(r'```json\s*', '', result)
            result = re.sub(r'```\s*$', '', result)
            
            # Try to find JSON object in the response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                result = json_match.group(0)
                self.logger.debug("Successfully extracted JSON from response")
            
            # Parse the JSON
            try:
                parsed_json = json.loads(result)
                self.logger.info("Successfully parsed JSON response")
                return parsed_json
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse JSON response: {str(e)}")
                # If JSON parsing fails, return a basic structure with the error
                return {
                    "error": "Failed to parse JSON response",
                    "raw_response": result[:200] + "..." if len(result) > 200 else result,
                    "parsed_fields": {
                        "date": None,
                        "title": None,
                        "author": None,
                        "recipient": None,
                        "main_points": [],
                        "summary": None
                    }
                }
        except Exception as e:
            self.logger.error(f"Error extracting fields: {str(e)}", exc_info=True)
            raise Exception(f"Error extracting fields: {str(e)}")

class DocumentProcessor:
    def __init__(self):
        self.logger = processor_logger
        self.extractor = ExtractorAgent()
        self.summarizer = SummarizerAgent()
        self.field_extractor = FieldExtractorAgent()
        self.logger.info("DocumentProcessor initialized")
    
    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """Process document through all agents and return results."""
        self.logger.info(f"Starting document processing for: {pdf_path}")
        try:
            # Extract text
            self.logger.debug("Starting text extraction phase")
            extracted_text = self.extractor.process(pdf_path)
            
            # Generate summary
            self.logger.debug("Starting summarization phase")
            summary = self.summarizer.process(extracted_text)
            
            # Extract fields
            self.logger.debug("Starting field extraction phase")
            fields = self.field_extractor.process(extracted_text)
            
            self.logger.info("Document processing completed successfully")
            return {
                "extracted_text": extracted_text,
                "summary": summary,
                "fields": fields
            }
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}", exc_info=True)
            raise Exception(f"Error processing document: {str(e)}") 