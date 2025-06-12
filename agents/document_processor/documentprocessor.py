# import os
# from unstract.llmwhisperer.client_v2 import LLMWhispererClientV2
# import boto3
# from .prompt import Prompt

# class DocumentProcessor:
#     def __init__(self, unstract_api_key: str, aws_bedrock_region: str, bedrock_model_id: str):
#         """
#         Initializes the DocumentProcessor with API keys, AWS region, and Bedrock model ID.

#         Args:
#             unstract_api_key (str): API key for the Unstract LLM Whisperer service.
#             aws_bedrock_region (str): AWS region where the Bedrock model is deployed (e.g., 'us-east-1').
#             bedrock_model_id (str): The specific identifier for the Bedrock model to use.
#         """
#         self.unstract_api_key = unstract_api_key
#         self.aws_bedrock_region = aws_bedrock_region
#         self.bedrock_model_id = bedrock_model_id
#         self.bedrock_client = boto3.client("bedrock-runtime", region_name=self.aws_bedrock_region)
        
#         self.system_instructions = Prompt


#     def _extract_text_from_pdf_and_save_to_ocr_txt(self, pdf_file_path: str, output_txt_path: str = "ocr.txt"):
#         """
#         Extracts text from a given PDF file using Unstract and saves the result to a .txt file.

#         Args:
#             pdf_file_path (str): The path to the input PDF file.
#             output_txt_path (str): The path where the extracted text will be saved. Defaults to "ocr.txt".

#         Returns:
#             bool: True if text extraction and saving were successful, False otherwise.
#         """
#         try:
#             client = LLMWhispererClientV2(api_key=self.unstract_api_key)
            
#             result = client.whisper(
#                 file_path=pdf_file_path,
#                 wait_for_completion=True,
#                 wait_timeout=180
#             )
            
#             if 'extraction' in result and 'result_text' in result['extraction']:
#                 extracted_text = result['extraction']['result_text']
#                 with open(output_txt_path, "w", encoding="utf-8") as f:
#                     f.write(extracted_text)
#                 return True
#             else:
#                 return False
                
#         except Exception:
#             return False

#     def process_pdf_to_json_string(self, pdf_file_path: str):
#         """
#         Processes a PDF document: extracts text, saves it to a temporary OCR file,
#         reads from that file, and then sends the content to AWS Bedrock for JSON structuring.

#         Args:
#             pdf_file_path (str): The path to the PDF file to process.

#         Returns:
#             str | None: A JSON string containing the structured information from Bedrock,
#                         or None if any step in the process fails.
#         """
#         ocr_txt_file = "ocr.txt"

#         # Extract text from PDF and saveing it.
#         extraction_success = self._extract_text_from_pdf_and_save_to_ocr_txt(pdf_file_path, ocr_txt_file)

#         if not extraction_success:
#             return None

#         # Read the extracted text from the saved .txt file.
#         ocr_text_content = None
#         try:
#             if not os.path.exists(ocr_txt_file):
#                 return None

#             with open(ocr_txt_file, "r", encoding="utf-8") as r:
#                 ocr_text_content = r.read()
#         except Exception:
#             return None
        
        

#         if not ocr_text_content:
#             return None

#         #  Sending the text content to Bedrock for JSON structuring.
#         conversation = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"text": self.system_instructions},
#                     {"text": ocr_text_content}
#                 ],
#             }
#         ]

#         try:
#             response = self.bedrock_client.converse(
#                 modelId=self.bedrock_model_id,
#                 messages=conversation,
#                 inferenceConfig={"maxTokens": 4000, "temperature": 0.3, "topP": 0.1} 
#             )
            
#             response_text = response["output"]["message"]["content"][0]["text"]
#             return response_text 
#         except Exception:
#           return None



# document_processor.py
import os
from unstract.llmwhisperer.client_v2 import LLMWhispererClientV2
import boto3
from .prompt import Prompt # Assuming 'Prompt' is a string variable containing your prompt

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
        
        # Ensure 'Prompt' is a string variable defined in your prompt.py file
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
        try:
            print(f"\n--- DEBUG: Starting _extract_text_from_pdf_and_save_to_ocr_txt ---")
            print(f"DEBUG: Processing PDF from path: {pdf_file_path}")
            print(f"DEBUG: Attempting to save OCR text to: {output_txt_path}")

            client = LLMWhispererClientV2(api_key=self.unstract_api_key)
            
            result = client.whisper(
                file_path=pdf_file_path,
                wait_for_completion=True,
                wait_timeout=180
            )
            
            print(f"DEBUG: Unstract API result received (partial, for brevity): {str(result)[:200]}...") # Print first 200 chars
            
            if 'extraction' in result and 'result_text' in result['extraction']:
                extracted_text = result['extraction']['result_text']
                
                # Check if extracted_text is empty or just whitespace before writing
                if not extracted_text.strip():
                    print(f"DEBUG: Extracted text from Unstract is empty or only whitespace. Not writing to file or writing empty content.")
                    # Return True here if it's considered a successful extraction even if empty
                    return True 
                else:
                    with open(output_txt_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)
                    print(f"DEBUG: Text successfully written to {output_txt_path}.")
                    print(f"DEBUG: Content length written: {len(extracted_text)} characters.")
                    print(f"DEBUG: Checking if file exists after write: {os.path.exists(output_txt_path)}")
                    return True
            else:
                print(f"DEBUG: Unstract result missing 'extraction' or 'result_text' key. Full result: {result}")
                return False
                
        except Exception as e: # Catch the exception details for more info
            print(f"DEBUG: An unexpected error occurred during Unstract extraction: {e}")
            return False
        finally:
            print(f"--- DEBUG: Finished _extract_text_from_pdf_and_save_to_ocr_txt ---\n")


    def process_pdf_to_json_string(self, pdf_file_path: str):
        """
        Processes a PDF document: extracts text, saves it to a temporary OCR file,
        reads from that file, and then sends the content to AWS Bedrock for JSON structuring.

        Args:
            pdf_file_path (str): The path to the PDF file to process.

        Returns:
            str | None: A JSON string containing the structured information from Bedrock,
                        or None if any step in the process fails.
        """
        ocr_txt_file = "ocr.txt"

        print(f"DEBUG: Calling _extract_text_from_pdf_and_save_to_ocr_txt for {pdf_file_path}")
        # Extract text from PDF and saving it.
        extraction_success = self._extract_text_from_pdf_and_save_to_ocr_txt(pdf_file_path, ocr_txt_file)

        if not extraction_success:
            print(f"DEBUG: Text extraction failed. Returning None.")
            return None

        # Read the extracted text from the saved .txt file.
        ocr_text_content = None
        try:
            print(f"DEBUG: Checking if {ocr_txt_file} exists before reading: {os.path.exists(ocr_txt_file)}")
            if not os.path.exists(ocr_txt_file):
                print(f"DEBUG: {ocr_txt_file} does not exist after extraction. Returning None.")
                return None

            with open(ocr_txt_file, "r", encoding="utf-8") as r:
                ocr_text_content = r.read()
            print(f"DEBUG: Read {len(ocr_text_content)} characters from {ocr_txt_file}.")
        except Exception as e:
            print(f"DEBUG: Error reading from {ocr_txt_file}: {e}. Returning None.")
            return None
        
        if not ocr_text_content: # If file was empty or not read properly
            print(f"DEBUG: ocr_text_content is empty after reading. Returning None.")
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
        print(f"DEBUG: Sending content to Bedrock. First 100 chars of OCR: {ocr_text_content[:100]}...")

        try:
            response = self.bedrock_client.converse(
                modelId=self.bedrock_model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 4000, "temperature": 0.3, "topP": 0.1} 
            )
            
            response_text = response["output"]["message"]["content"][0]["text"]
            print(f"DEBUG: Received response from Bedrock (partial): {response_text[:200]}...")
            return response_text 
        except Exception as e:
          print(f"DEBUG: Error during Bedrock conversation: {e}. Returning None.")
        return None