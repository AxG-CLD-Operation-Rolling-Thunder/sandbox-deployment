"""
Invoice Processing Tool for extracting structured data from invoice files
Uses Gemini 2.5 Flash for initial extraction and Gemini 2.5 Pro for complex cases
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import google.generativeai as genai

import io
import requests
from Invoice_agent.prompts import prompts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LineItem(BaseModel):
    """Model for individual line items in an invoice"""
    description: str
    quantity: Optional[float] = 1.0
    unit_price: Optional[float] = None
    total: float
    
    @validator('total', pre=True)
    def calculate_total(cls, v, values):
        if v is None and values.get('quantity') and values.get('unit_price'):
            return values['quantity'] * values['unit_price']
        return v


class InvoiceData(BaseModel):
    """Structured model for extracted invoice data"""
    vendor_name: str
    invoice_date: str
    total_amount: float
    tax_amount: Optional[float] = 0.0
    currency: str = "USD"
    line_items: List[LineItem] = []
    
    @validator('invoice_date')
    def validate_date_format(cls, v):
        """Ensure date is in YYYY-MM-DD format"""
        try:
            # Try to parse various date formats and standardize
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y']:
                try:
                    date_obj = datetime.strptime(v, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return v  # Return as-is if no format matches
        except Exception:
            return v


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
        logger.info("file_data_parse", file_data)
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

        # For known image/document types, always treat as binary
        binary_mime_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
        'application/pdf', 'application/vnd.google-apps.presentation',
        'application/vnd.google-apps.spreadsheet', 
        'application/vnd.google-apps.document'
        ]
    
        if mime_type in binary_mime_types:
            # Always treat these as binary data
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
        content_parts = self._get_content_parts(file_data, mime_type, prompts.INVOICE_EXTRACTION_PROMPT)
    
        response = self.flash_model.generate_content(content_parts)
        return self._parse_response(response.text)

    def _extract_with_pro(self, file_data: bytes, mime_type: str) -> InvoiceData:
        """Extract invoice data using Gemini 2.5 Pro for complex cases"""
        content_parts = self._get_content_parts(file_data, mime_type, prompts.INVOICE_EXTRACTION_PROMPT_DETAILED)

        response = self.pro_model.generate_content(
            content_parts,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
            "max_output_tokens": 2048
        }
    )
        return self._parse_response(response.text)

    def is_text_content(self, data: bytes) -> bool:
        """
    Heuristic to check if the bytes represent text content (e.g., from OCR).
    This could be a simple check for a high density of printable characters.
    """
    # A simple check: if the first few bytes are not common file headers
        common_headers = [b'%PDF', b'\x89PNG', b'\xFF\xD8\xFF']
        if any(data.startswith(header) for header in common_headers):
            return False
        # If the data starts with plain text, it is likely the preprocessed OCR result
        return True

    def _parse_response(self, response_text: str) -> InvoiceData:
        """Parse and validate the JSON response from Gemini"""
        try:
            # Clean te response text
            cleaned_text = response_text.strip()
            
            # Remove potential markdown code blocks
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Validate with Pydantic
            invoice_data = InvoiceData(**data)
            
            return invoice_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
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
        
        # Check if line items sum matches total (within 1% tolerance)
        if invoice_data.line_items:
            line_items_sum = sum(item.total for item in invoice_data.line_items)
            expected_total = line_items_sum + invoice_data.tax_amount
            
            if abs(expected_total - invoice_data.total_amount) > (invoice_data.total_amount * 0.01):
                warnings.append(f"Line items sum ({expected_total}) doesn't match total amount ({invoice_data.total_amount})")
        
        # Validate date is not in the future
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


# Convenience function for direct usage
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
    # Map file type to mime type
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