
"""
Invoice Processing Tool for extracting structured data from invoice files
Uses Gemini 2.5 Flash for initial extraction and Gemini 2.5 Pro for complex cases
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, field_validator, FieldValidationInfo
from google import genai
from google.genai import types
from ..prompts import invoice_extraction_promot_with_flash, invoice_extraction_prompt_with_pro

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTRACTION_CONFIG = types.GenerateContentConfig(
    temperature=0.0,
    top_p=0.95,
    top_k=1,
    max_output_tokens=2048,
    candidate_count=1
)

class LineItem(BaseModel):
    """Model for individual line items in an invoice"""
    description: str
    quantity: Optional[float] = 1.0
    unit_price: Optional[float] = None
    total: float
    
    @field_validator('total', mode='before')
    @classmethod
    def calculate_total(cls, v, info: FieldValidationInfo):
        if v is None and 'quantity' in info.data and 'unit_price' in info.data:
            return info.data['quantity'] * info.data['unit_price']
        return v


class InvoiceData(BaseModel):
    """Structured model for extracted invoice data"""
    vendor_name: str
    invoice_date: str
    total_amount: float
    tax_amount: Optional[float] = 0.0
    currency: str = "USD"
    line_items: List[LineItem] = []
    
    @field_validator('invoice_date')
    @classmethod
    def validate_date_format(cls, v):
        """Ensure date is in YYYY-MM-DD format"""
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y']:
            try:
                date_obj = datetime.strptime(v, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError("Invalid date format. Expected one of YYYY-MM-DD, MM/DD/YYYY, etc.")

class InvoiceParser:
    """Main class for parsing invoices using Gemini models"""
    
    def __init__(self):
        """
        Initialize the parser with Gemini API configuration.
        The client automatically uses Application Default Credentials (ADC).
        To configure ADC for local development, run:
        `gcloud auth application-default login`
        """
        self.client = genai.Client()
        self.flash_model_name = 'gemini-2.5-flash'
        self.pro_model_name = 'gemini-2.5-pro'
        
    def parse_invoice(self, file_data: bytes, mime_type: str) -> InvoiceData:
        """
        Parse invoice file and extract structured data
        
        Args:
            file_data: Raw file content as bytes
            file_type: Type of file (pdf, jpeg, png, docs, sheets, slides)
            
        Returns:
            InvoiceData: Structured invoice data
            
        Raises:
            ValueError: If parsing fails after both model attempts
        """

        # First attempt with Gemini 2.5 Flash
        try:
            result = self._extract_with_flash(file_data, mime_type)
            logger.info("Successfully extracted invoice data with Gemini Flash")
            return result
        except Exception as e:
            logger.warning(f"Flash extraction failed: {str(e)}, escalating to Pro model")
            
            # Escalate to Gemini 2.5 Pro for complex cases
            try:
                result = self._extract_with_pro(file_data, mime_type)
                logger.info("Successfully extracted invoice data with Gemini Pro")
                return result
            except Exception as pro_error:
                logger.error(f"Pro extraction also failed: {str(pro_error)}")
                raise ValueError(f"Failed to extract invoice data: {str(pro_error)}")
    
    def _get_mime_type(self, file_type: str) -> str:
        """Get MIME type from file type"""
        logging.info("file_type_to_map_mime_type", file_type)
        mime_type_map = {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "png": "image/png",
            "pdf": "application/pdf",
            "slides": "application/vnd.google-apps.presentation",
            "sheets": "application/vnd.google-apps.spreadsheet",
            "docs": "application/vnd.google-apps.document"
        }
        return mime_type_map.get(file_type.lower(), "application/octet-stream")
    
    def _get_content_parts(self, file_data: bytes, mime_type: str, prompt: str) -> List[Any]:
        """Create proper content parts for Gemini API call."""
        content_parts = [prompt]

        binary_mime_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
            'application/pdf', 'application/vnd.google-apps.presentation',
            'application/vnd.google-apps.spreadsheet',  
            'application/vnd.google-apps.document'
        }

        if mime_type in binary_mime_types:
            content_parts.append(types.Part.from_bytes(data=file_data, mime_type=mime_type))
        
        elif self.is_text_content(file_data):
            try:
                decoded_text = file_data.decode('utf-8')
                content_parts.append(decoded_text)
            except UnicodeDecodeError:
                content_parts.append(types.Part.from_bytes(data=file_data, mime_type=mime_type or 'application/octet-stream'))
        
        else:
            content_parts.append(types.Part.from_bytes(data=file_data, mime_type=mime_type))

        return content_parts


    def _extract_with_flash(self, file_data: bytes, mime_type: str) -> InvoiceData:
        """Extract invoice data using Gemini 2.5 Flash"""
        content_parts = self._get_content_parts(file_data, mime_type, invoice_extraction_promot_with_flash.INVOICE_EXTRACTION_PROMPT)

        try:
            logger.info(type(file_data))
            logger.info(f"Content parts for Flash extraction: {[type(part) for part in content_parts]}")
            logger.info(f"MIME type for Flash extraction: {mime_type}")
        except Exception:
            logger.error(f"Error occurred while logging Flash extraction details")

        try:
            response = self.client.models.generate_content(
                model = self.flash_model_name,
                contents=content_parts,
                config=EXTRACTION_CONFIG
            )
            
            logger.info(f"Response object: {response}")
            logger.info(f"Response text: {response.text}")
            
            if not response.text:
                raise ValueError("No text content returned from Flash model")
            
            return self._parse_response(response.text)
        except Exception as e:
            logger.error(f"Flash extraction error: {str(e)}")
            raise

    def _extract_with_pro(self, file_data: bytes, mime_type: str) -> InvoiceData:
        """Extract invoice data using Gemini 2.5 Pro for complex cases"""
        content_parts = self._get_content_parts(file_data, mime_type, invoice_extraction_prompt_with_pro.INVOICE_EXTRACTION_PROMPT_DETAILED)
        
        pro_safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
            )
        ]

        pro_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=1.0,
            top_k=1,
            max_output_tokens=2048,
            candidate_count=1,
            safety_settings=pro_safety_settings
        )

        try:
            response = self.client.models.generate_content(
                model = self.pro_model_name,
                contents=content_parts,
                config=pro_config
            )
            
            if not response.text:
                if hasattr(response, 'prompt_feedback'):
                    logger.error(f"Pro model prompt feedback: {response.prompt_feedback}")
                raise ValueError("No text content returned from Pro model")
            
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Pro extraction error: {str(e)}")
            raise

    def is_text_content(self, data: bytes) -> bool:
        """
        Heuristic to check if the bytes represent text content (e.g., from OCR).
        This could be a simple check for a high density of printable characters.
        """
        common_headers = [b'%PDF', b'\x89PNG', b'\xFF\xD8\xFF']
        if any(data.startswith(header) for header in common_headers):
            return False
        return True

    def _parse_response(self, response_text: str) -> InvoiceData:
        """Parse and validate the JSON response from Gemini"""
        try:
            if not response_text:
                raise ValueError("Empty response from model")
            cleaned_text = response_text.strip()
            
            # Remove potential markdown code blocks
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            quote_count = cleaned_text.count('"')
            if quote_count % 2 != 0:
                cleaned_text = cleaned_text.rstrip() + '"'
            
            cleaned_text = re.sub(r',\s*}', '}', cleaned_text)
            cleaned_text = re.sub(r',\s*]', ']', cleaned_text)
            data = json.loads(cleaned_text)
            
            invoice_data = InvoiceData(**data)
            
            return invoice_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")  # Log first 500 chars
            raise ValueError(f"Invalid JSON response from model: {e}")
        except Exception as e:
            logger.error(f"Failed to validate invoice data: {e}")
            raise ValueError(f"Invalid invoice data structure: {e}")
    
    def validate_extraction(self, invoice_data: InvoiceData) -> Dict[str, Any]:
        """
        Validate the extracted data and return validation results
        
        Args:
            invoice_data: Extracted invoice data
            
        Returns:
            Dictionary with validation status and any warnings
        """
        warnings = []
        
        if not invoice_data.vendor_name:
            warnings.append("Vendor name is missing")
        
        if invoice_data.total_amount <= 0:
            warnings.append("Total amount is zero or negative")
        
        if invoice_data.line_items:
            line_items_sum = sum(item.total for item in invoice_data.line_items)
            expected_total = line_items_sum + invoice_data.tax_amount
            
            if abs(expected_total - invoice_data.total_amount) > (invoice_data.total_amount * 0.01):
                warnings.append(f"Line items sum ({expected_total}) doesn't match total amount ({invoice_data.total_amount})")
        
        try:
            invoice_date = datetime.strptime(invoice_data.invoice_date, '%Y-%m-%d')
            if invoice_date > datetime.now():
                warnings.append("Invoice date is in the future")
        except:
            warnings.append("Invalid date format")
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "data": invoice_data.dict()
        }


def parse_invoice(file_data: bytes, file_type: str, mime_type: str) -> Dict[str, Any]:
    """
    Parse an invoice file and return structured data
    
    Args:
        file_data: Raw file content
        file_type: Type of file (jpeg, png, pdf, docs, sheets, slides)
        
    Returns:
        Dictionary containing the parsed invoice data and validation results
    """
    mime_type_map = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "pdf": "application/pdf",
        "slides": "application/vnd.google-apps.presentation",
        "sheets": "application/vnd.google-apps.spreadsheet",
        "docs": "application/vnd.google-apps.document"
    }

    parser = InvoiceParser()  # No API key needed here
    
    try:
        invoice_data = parser.parse_invoice(file_data, mime_type)
        validation_result = parser.validate_extraction(invoice_data)
        
        return {
            "success": True,
            "data": invoice_data.dict(),
            "validation": validation_result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }
