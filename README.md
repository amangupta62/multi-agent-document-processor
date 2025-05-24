# Multi-Agent Document Processing System

This system uses multiple LLM-powered agents to process PDF documents, extract text, generate summaries, and identify key fields.

## Features

- PDF text extraction
- Text summarization using LLaMA 3
- Key field extraction and structuring
- Multi-tab Streamlit interface
- Real-time processing status

## Prerequisites

- Python 3.8+
- Ollama with LLaMA 3 model installed
- pip (Python package manager)

## Setup

1. Install Ollama and pull the LLaMA 3 model:
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your browser (default: http://localhost:8501)
2. Upload a PDF document using the file uploader
3. Click "Extract" to start processing
4. View results in the respective tabs:
   - Raw extracted text
   - Generated summary
   - Extracted key fields

## Project Structure

- `app.py`: Main Streamlit application
- `agents.py`: Agent definitions and processing logic
- `requirements.txt`: Python dependencies 