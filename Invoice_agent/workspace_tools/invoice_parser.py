"""
Invoice Processing Tool for extracting structured data from invoice files
Uses Gemini 2.5 Flash for initial extraction and Gemini 2.5 Pro for complex cases
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
import google.generativeai as genai

import io
import requests
from  invoice_agent.prompts import invoice_extraction_promot_with_flash, invoice_extraction_prompt_with_pro

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTRACTION_CONFIG = {"temperature": 0.0,
                "top_p": 0.95,
                "top_k": 1,
                "max_output_tokens": 2048,
                "candidate_count": 1 }

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
        # If no format matches, let Pydantic's type validation handle it
        # or raise a specific error.
        raise ValueError("Invalid date format. Expected one of YYYY-MM-DD, MM/DD/YYYY, etc.")

class InvoiceParser:
    """Main class for parsing invoices using Gemini models"""
    
    def __init__(self, api_key: str):
        """
        Initialize the parser with Gemini API configuration
        
        Args:
            api_key: Google AI API key for Gemini
        """
        genai.configure(api_key=api_key)
        self.flash_model = genai.GenerativeModel('gemini-2.5-flash')
        self.pro_model = genai.GenerativeModel('gemini-2.5-pro')
        
    def parse_invoice(self, file_data: bytes, file_type: str) -> InvoiceData:
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
        logger.info(f"Processing invoice with file type: {file_type}")
        mime_type = self._get_mime_type(file_type)
        
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
        """Helper function to create the correct content parts for the Gemini API call."""
        content_parts = [prompt]

        binary_mime_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
        'application/pdf', 'application/vnd.google-apps.presentation',
        'application/vnd.google-apps.spreadsheet', 
        'application/vnd.google-apps.document'
        ]
    
        if mime_type in binary_mime_types:
            content_parts.append({
            'mime_type': mime_type,
            'data': file_data
        })
        elif self.is_text_content(file_data):
            try:
                # Try to decode as UTF-8
                decoded_text = file_data.decode('utf-8')
                content_parts.append(decoded_text)
            except UnicodeDecodeError:
                # If decoding fails, treat as binary
                logger.warning(f"Failed to decode as UTF-8, treating as binary with mime_type: {mime_type}")
                content_parts.append({
                'mime_type': mime_type or 'application/octet-stream',
                'data': file_data
             })
        else:
            # Binary data
            content_parts.append({
            'mime_type': mime_type,
            'data': file_data
        })

        return content_parts

    def _extract_with_flash(self, file_data: bytes, mime_type: str) -> InvoiceData:
        """Extract invoice data using Gemini 2.5 Flash"""
        content_parts = self._get_content_parts(file_data, mime_type, invoice_extraction_promot_with_flash.INVOICE_EXTRACTION_PROMPT)
    
        try:
            response = self.flash_model.generate_content(
            content_parts,
            generation_config= EXTRACTION_CONFIG
            )
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Has parts: {bool(response.parts)}")
            logger.info(f"Parts count: {len(response.parts) if response.parts else 0}")  
            if not response.parts:
                raise ValueError("No response parts returned from Flash model")
            
            if not hasattr(response, 'text') or not response.text:
                raise ValueError("No text in response from Flash model")
            
            return self._parse_response(response.text)
        except Exception as e:
            logger.error(f"Flash extraction error: {str(e)}")
            raise
    def _extract_with_pro(self, file_data: bytes, mime_type: str) -> InvoiceData:
        """Extract invoice data using Gemini 2.5 Pro for complex cases"""
        content_parts = self._get_content_parts(file_data, mime_type, invoice_extraction_prompt_with_pro.INVOICE_EXTRACTION_PROMPT_DETAILED)
        safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
        try:
            response = self.pro_model.generate_content(
            content_parts,
                   generation_config={
                "temperature": 0.0,
                "top_p": 1.0,        
                "top_k": 1,         
                "max_output_tokens": 2048,
                "candidate_count": 1
            }
        )
            safety_settings=safety_settings
            if not response.parts:
                if hasattr(response, 'prompt_feedback'):
                    logger.error(f"Pro model prompt feedback: {response.prompt_feedback}")
                raise ValueError("No response parts returned from Pro model")
            
            response_text = None
            if hasattr(response, 'text'):
                response_text = response.text
            elif response.parts and len(response.parts) > 0:
                response_text = response.parts[0].text
            
            if not response_text:
                raise ValueError("No text content in Pro model response")
            
            return self._parse_response(response_text)
        
        except Exception as e:
            logger.error(f"Pro extraction error: {str(e)}")
            if hasattr(response, 'candidates') and response.candidates:
                for i, candidate in enumerate(response.candidates):
                    logger.error(f"Candidate {i} finish reason: {candidate.finish_reason}")
                    if hasattr(candidate, 'safety_ratings'):
                        logger.error(f"Candidate {i} safety ratings: {candidate.safety_ratings}")
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


def parse_invoice(file_data: bytes, file_type: str, api_key: str) -> Dict[str, Any]:
    """
    Parse an invoice file and return structured data
    
    Args:
        file_data: Raw file content
        file_type: Type of file (jpeg, png, pdf, docs, sheets, slides)
        api_key: Google AI API key
        
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
    mime_type = mime_type_map.get(file_type.lower(), "image/jpeg")
    parser = InvoiceParser(api_key)
    
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
