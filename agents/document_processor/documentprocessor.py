import os
from unstract.llmwhisperer.client_v2 import LLMWhispererClientV2
import boto3
from .prompt import Prompt 

class DocumentProcessor:
    def __init__(self, unstract_api_key: str, aws_bedrock_region: str, bedrock_model_id: str):
        """
        Initializes the DocumentProcessor with API keys, AWS region, and Bedrock model ID.

        Args:
            unstract_api_key (str): API key for the Unstract LLM Whisperer service.
            aws_bedrock_region (str): AWS region where the Bedrock model is deployed (e.g., 'us-east-1').
            bedrock_model_id (str): The specific identifier for the Bedrock model to use.
        """
        self.unstract_api_key = unstract_api_key
        self.aws_bedrock_region = aws_bedrock_region
        self.bedrock_model_id = bedrock_model_id
        self.bedrock_client = boto3.client("bedrock-runtime", region_name=self.aws_bedrock_region)
        
        self.system_instructions = Prompt


    def _extract_text_from_pdf_and_save_to_ocr_txt(self, pdf_file_path: str, output_txt_path: str = "ocr.txt"):
        """
        Extracts text from a given PDF file using Unstract and saves the result to a .txt file.

        Args:
            pdf_file_path (str): The path to the input PDF file.
            output_txt_path (str): The path where the extracted text will be saved. Defaults to "ocr.txt".

        Returns:
            bool: True if text extraction and saving were successful, False otherwise.
        """
        
        # Getting the directory of the current document_processor.py file
        current_processor_dir = os.path.dirname(os.path.abspath(__file__))

        # Joining the directory with the filename "ocr.txt"
        actual_output_file_path = os.path.join(current_processor_dir, output_txt_path)
        
        try:
            client = LLMWhispererClientV2(api_key=self.unstract_api_key)
            
            result = client.whisper(
                file_path=pdf_file_path,
                wait_for_completion=True,
                wait_timeout=180
            )
            
            if 'extraction' in result and 'result_text' in result['extraction']:
                extracted_text = result['extraction']['result_text']
                if extracted_text.strip():
                    
                    with open(actual_output_file_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)
                    
                return True
            else:
                return False
                
        except Exception:
            return False

    def process_pdf_to_json_string(self, pdf_file_path: str):
        ocr_txt_filename = "ocr.txt" # Keep this as just the filename

        # Get the directory of the current document_processor.py file
        current_processor_dir = os.path.dirname(os.path.abspath(__file__))
        actual_ocr_read_path = os.path.join(current_processor_dir, ocr_txt_filename)
        
        # Extracting text from PDF and saveing it.
        extraction_success = self._extract_text_from_pdf_and_save_to_ocr_txt(pdf_file_path, ocr_txt_filename)

        if not extraction_success:
            return None

        # Read the extracted text from the saved .txt file using its absolute path.
        ocr_text_content = None
        try:
            if not os.path.exists(actual_ocr_read_path):
                return None

            with open(actual_ocr_read_path, "r", encoding="utf-8") as r:
                ocr_text_content = r.read()
        except Exception:
            return None
        
        if not ocr_text_content:
            return None

        # Sending the text content to Bedrock for JSON structuring.
        conversation = [
            {
                "role": "user",
                "content": [
                    {"text": self.system_instructions},
                    {"text": ocr_text_content}
                ],
            }
        ]

        try:
            response = self.bedrock_client.converse(
                modelId=self.bedrock_model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 4000, "temperature": 0.3, "topP": 0.1} 
            )
            
            response_text = response["output"]["message"]["content"][0]["text"]
            return response_text 
        except Exception:
            return None