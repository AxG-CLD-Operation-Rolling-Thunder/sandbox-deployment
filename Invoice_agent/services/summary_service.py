"""
Summary generation service
"""
import os
import json
import logging
from datetime import datetime
import google.generativeai as genai
from ..prompts import prompts

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self, session_service):
        self.session = session_service
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            
    def generate(self, data: dict = None) -> dict:
        """Generate summary of all processed invoices"""
        if not self.session.invoices:
            return {
                "status": "error",
                "message": "No invoices processed yet. Please upload invoice files first."
            }
            
        if not self.api_key:
            return {
                "status": "error",
                "message": "API key not configured."
            }
            
        try:
            invoices_json = self._prepare_invoices_json()
            summary_text = self._generate_summary_text(invoices_json)
            totals = self._calculate_totals()
            
            return {
                "status": "success",
                "summary": summary_text,
                "invoice_count": len(self.session.invoices),
                "totals": totals["by_currency"],
                "total_tax": totals["tax_by_currency"]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate summary: {str(e)}"
            }
            
    def _prepare_invoices_json(self) -> str:
        """Prepare invoices data as JSON for the prompt"""
        return json.dumps([{
            "vendor_name": inv.get('vendor_name', 'Unknown'),
            "invoice_date": inv.get('invoice_date', 'N/A'),
            "total_amount": float(inv.get('total_amount', 0)),
            "tax_amount": float(inv.get('tax_amount', 0)),
            "currency": inv.get('currency', 'USD'),
            "line_items": inv.get('line_items', [])
        } for inv in self.session.invoices], indent=2)
        
    def _generate_summary_text(self, invoices_json: str) -> str:
        """Generate summary text using Gemini"""
        prompt = prompts.SUMMARY_GENERATION_PROMPT.format(
            invoice_count=len(self.session.invoices),
            invoices_json=invoices_json,
            current_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048
            }
        )
        
        return response.text
        
    def _calculate_totals(self) -> dict:
        """Calculate totals by currency"""
        totals_by_currency = {}
        tax_by_currency = {}
        
        for invoice in self.session.invoices:
            currency = invoice.get('currency', 'USD')
            amount = float(invoice.get('total_amount', 0))
            tax = float(invoice.get('tax_amount', 0))
            
            if currency not in totals_by_currency:
                totals_by_currency[currency] = 0
                tax_by_currency[currency] = 0
                
            totals_by_currency[currency] += amount
            tax_by_currency[currency] += tax
            
        return {
            "by_currency": totals_by_currency,
            "tax_by_currency": tax_by_currency
        }