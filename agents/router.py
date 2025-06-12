import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
dontenv_file_path = os.path.join(current_dir, "client", ".env")

load_dotenv(dotenv_path=dontenv_file_path)

# Importing the DocumentProcessor class from the 'output' module
from  agents.document_processor.documentprocessor  import DocumentProcessor


# Retrieveing API keys and model identifiers from environment variables
UNSTRACT_API_KEY = os.getenv("UNSTRACT-API-KEY")
AWS_BEDROCK_REGION = os.getenv("AWS_BEDROCK_REGION")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

# Validateing that essential environment variables are set
if not UNSTRACT_API_KEY:
    raise ValueError("UNSTRACT-API-KEY environment variable is not set.")
if not AWS_BEDROCK_REGION:
    raise ValueError("AWS_BEDROCK_REGION environment variable is not set.")
if not BEDROCK_MODEL_ID:
    raise ValueError("BEDROCK_MODEL_ID environment variable is not set.")

# Initializing the FastAPI application
app = FastAPI(
    title="Bank Document Parser API",
    description="API to extract and structure information from bank application PDFs."
    
)

# Initializing the DocumentProcessor instance upon application startup
try:
    doc_processor = DocumentProcessor(
        unstract_api_key=UNSTRACT_API_KEY,
        aws_bedrock_region=AWS_BEDROCK_REGION,
        bedrock_model_id=BEDROCK_MODEL_ID
    )
except Exception:
    # If DocumentProcessor initialization fails, raise a runtime error to prevent app startup
    raise RuntimeError("Application failed to start due to DocumentProcessor initialization error.")


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File()):
    """
    Handles PDF file uploads. The uploaded PDF is processed to extract text,
    which is then sent to a Bedrock model for structured JSON output.

    Args:
        file (UploadFile): The PDF file uploaded by the client.

    Returns:
        JSONResponse: A JSON object containing the extracted and structured data.

    Raises:
        HTTPException: If an error occurs during file processing or Bedrock interaction.
    """
    # Create a temporary path for the uploaded PDF file
    temp_pdf_path = f"uploaded_temp_{file.filename}" 
    
    try:
        # Save the content of the uploaded file to the temporary path
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the temporary PDF file using the DocumentProcessor
        json_output_string = doc_processor.process_pdf_to_json_string(temp_pdf_path)

        if json_output_string:
            # Convert the JSON string from Bedrock into a Python dictionary
            # then return it as a JSONResponse to ensure correct content type.
            import json 
            try:
                parsed_json = json.loads(json_output_string)
                return JSONResponse(content=parsed_json)
            except json.JSONDecodeError:
                # If Bedrock's response is not valid JSON, raise an error
                raise HTTPException(status_code=500, detail="Bedrock response was not a valid JSON string.")

        else:
            # If no JSON output string is received from the processor, raise an error
            raise HTTPException(status_code=500, detail="Failed to process PDF and extract information.")

    except HTTPException:
        # Re-raise any HTTPException errors caught
        raise
    except Exception:
        # Catch any other unexpected errors during processing and return a 500 error
        raise HTTPException(status_code=500, detail="An internal server error occurred during PDF processing.")
    finally:
        # Cleaning up the temporary PDF file if it is exist
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

