"""
Invoice processing service
"""
import base64
import logging
from typing import Dict, Any
from ..workspace_tools.invoice_parser import parse_invoice
from ..utils.file_detector import detect_file_type

logger = logging.getLogger(__name__)

class InvoiceService:
    def __init__(self, session_service):
        self.session = session_service

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an uploaded invoice"""
        logger.info(f"Processing invoice. Current invoice count: {self.session.get_invoice_count()}")
        logging.info("file_data_recieved_from_agent", data.get('file_data'))

        file_data = self._extract_file_data(data)
        if not file_data:
            return {
                "status": "error",
                "message": "No file data found. Please upload an invoice file."
            }
            
        file_type = detect_file_type(file_data)
        result = parse_invoice(file_data, file_type, data.get('mimetype', 'application/pdf'))
        
        if result["success"]:
            invoice_data = result["data"]
            self.session.add_invoice(invoice_data)
            
            return {
                "status": "success",
                "message": self._format_success_message(invoice_data),
                "data": invoice_data,
                "validation": result.get("validation", {}),
                "session_info": {
                    "total_invoices": self.session.get_invoice_count()
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to process invoice: {result.get('error', 'Unknown error')}"
            }

    def _extract_file_data(self, data: Dict[str, Any]) -> bytes:
        """Extract file data from various input formats"""
        if isinstance(data, bytes):
            return data
            
        if "file_data" in data:
            file_data_obj = data["file_data"]
            if isinstance(file_data_obj, bytes):
                return file_data_obj
            elif isinstance(file_data_obj, str):
                try:
                    return base64.b64decode(file_data_obj)
                except:
                    return file_data_obj.encode()
                    
        return None
        
    def _format_success_message(self, invoice_data: dict) -> str:
        """Format success message for processed invoice"""
        vendor = invoice_data.get('vendor_name', 'Unknown')
        amount = invoice_data.get('total_amount', 0)
        currency = invoice_data.get('currency', 'USD')
        return f"Invoice processed: {vendor} - {amount} {currency}"
