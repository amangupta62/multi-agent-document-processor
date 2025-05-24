import streamlit as st
import tempfile
import os
from agents import DocumentProcessor
import json
import time

st.set_page_config(
    page_title="Document Processing System",
    page_icon="📄",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def update_processing_status(status, progress_bar, status_text):
    """Update the processing status and progress bar."""
    status_text.text(status)
    progress_bar.progress(min(progress_bar.progress + 0.25, 1.0))

def main():
    st.title("📄 Multi-Agent Document Processing System")
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = ""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload", 
        "⚙️ Processing", 
        "📝 Extracted Text", 
        "📋 Summary", 
        "🔑 Key Fields"
    ])

    with tab1:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            if st.button("Extract"):
                # Switch to processing tab
                st.session_state.current_step = 0
                st.switch_page("⚙️ Processing")
                
                with tab2:
                    st.header("Processing Status")
                    
                    # Create progress bar and status text
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Save uploaded file
                        update_processing_status("📥 Saving uploaded file...", progress_bar, status_text)
                        pdf_path = save_uploaded_file(uploaded_file)
                        
                        if pdf_path:
                            # Initialize processor
                            processor = DocumentProcessor()
                            
                            # Extract text
                            update_processing_status("📄 Extracting text from PDF...", progress_bar, status_text)
                            extracted_text = processor.extractor.process(pdf_path)
                            
                            # Generate summary
                            update_processing_status("📝 Generating summary...", progress_bar, status_text)
                            summary = processor.summarizer.process(extracted_text)
                            
                            # Extract fields
                            update_processing_status("🔑 Extracting key fields...", progress_bar, status_text)
                            fields = processor.field_extractor.process(extracted_text)
                            
                            # Store results
                            st.session_state.results = {
                                "extracted_text": extracted_text,
                                "summary": summary,
                                "fields": fields
                            }
                            
                            # Clean up temporary file
                            os.unlink(pdf_path)
                            
                            # Show completion status
                            update_processing_status("✅ Processing completed successfully!", progress_bar, status_text)
                            time.sleep(1)  # Give user time to see completion
                            
                            # Switch to results tab
                            st.switch_page("📝 Extracted Text")
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
                        progress_bar.progress(0)
                        status_text.text("❌ Processing failed!")

    with tab2:
        st.header("Processing Status")
        if st.session_state.results:
            st.success("✅ Document processing completed!")
        else:
            st.info("No document processed yet. Please upload a document in the Upload tab.")

    with tab3:
        st.header("Extracted Text")
        if st.session_state.results:
            st.text_area("Raw Text", st.session_state.results["extracted_text"], height=400)
        else:
            st.info("No text extracted yet. Please upload and process a document.")

    with tab4:
        st.header("Summary")
        if st.session_state.results:
            st.text_area("Document Summary", st.session_state.results["summary"], height=400)
        else:
            st.info("No summary available yet. Please upload and process a document.")

    with tab5:
        st.header("Key Fields")
        if st.session_state.results:
            # Format JSON for better display
            formatted_json = json.dumps(st.session_state.results["fields"], indent=2)
            st.json(formatted_json)
            
            # Add download button for JSON
            st.download_button(
                label="Download JSON",
                data=formatted_json,
                file_name="extracted_fields.json",
                mime="application/json"
            )
        else:
            st.info("No fields extracted yet. Please upload and process a document.")

if __name__ == "__main__":
    main() 