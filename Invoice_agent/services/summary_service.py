"""
Summary generation service
"""
import os
import json
import logging
from datetime import datetime
from google import genai
from google.genai import types
from ..prompts import summary_generation_prompt

logger = logging.getLogger(__name__)

SUMMARY_CONFIG = types.GenerateContentConfig(
    temperature=0.0,
    top_p=0.9,
    top_k=40,
    max_output_tokens=2048
)

class SummaryService:
    def __init__(self, session_service):
        self.session = session_service
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client()
            self.model_name = 'gemini-2.5-pro'
            
    def generate(self, data: dict = None) -> dict:
        """Generate summary of all processed invoices in current session"""
        invoices = self.session.invoices
        logger.info(f"Generating summary for {len(invoices)} invoices from current session")
        
        if not invoices:
            return {
                "status": "error",
                "message": "No invoices processed yet in this session. Please upload invoice files first."
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
                "invoice_count": len(invoices),
                "totals": totals["by_currency"],
                "total_tax": totals["tax_by_currency"],
                "session_info": self.session.get_session_info()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate summary: {str(e)}"
            }

    def _prepare_invoices_json(self) -> str:
        """Prepare invoices data as JSON for the prompt"""
        invoices = self.session.invoices
        return json.dumps([{
            "vendor_name": inv.get('vendor_name', 'Unknown'),
            "invoice_date": inv.get('invoice_date', 'N/A'),
            "total_amount": float(inv.get('total_amount', 0)),
            "tax_amount": float(inv.get('tax_amount', 0)),
            "currency": inv.get('currency', 'USD'),
            "line_items": inv.get('line_items', [])
        } for inv in invoices], indent=2)
        
    def _generate_summary_text(self, invoices_json: str) -> str:
        """Generate summary text using Gemini"""
        invoices = self.session.invoices

        prompt = summary_generation_prompt.SUMMARY_GENERATION_PROMPT.format(
            invoice_count=len(invoices),
            invoices_json=invoices_json,
            current_date=datetime.now().strftime('%Y-%m-%d')
        )
    
        logger.info(f"Generating summary for {len(invoices)} invoices")
        
        safety_settings = [
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

        # summary_config = types.GenerateContentConfig(
        #     **SUMMARY_CONFIG.model_dump(),
        #     safety_settings=safety_settings
        # )

        summary_config = types.GenerateContentConfig(
                temperature=0.0,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
                safety_settings=safety_settings
        )
        response = self.client.models.generate_content(
            model = self.model_name,
            contents=prompt,
            config=summary_config,
        )       
    
        try:
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"Could not access response.text: {e}")
    
        logger.warning("Using fallback summary due to invalid response")
        return self._generate_simple_summary()
        
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
        
    def _generate_simple_summary(self) -> str:
        """Generate a simple summary without using Gemini"""
        invoices = self.session.invoices
        lines = []
    
        lines.append(f"EXPENSE SUMMARY")
        lines.append("")
        lines.append("| Vendor_name | Invoice_date | Total_amount | Tax_amount | Currency | LineItems |")
        lines.append("|-------------|--------------|--------------|------------|----------|-----------|")
    
        totals_by_currency = {}
        tax_by_currency = {}
    
        for invoice in invoices:
            vendor = invoice.get('vendor_name', 'Unknown')
            date = invoice.get('invoice_date', 'N/A')
            amount = float(invoice.get('total_amount', 0))
            tax = float(invoice.get('tax_amount', 0))
            currency = invoice.get('currency', 'USD')
        
            if currency not in totals_by_currency:
                totals_by_currency[currency] = 0
                tax_by_currency[currency] = 0
            totals_by_currency[currency] += amount
            tax_by_currency[currency] += tax
        
            line_items_desc = "General expense"
            if invoice.get('line_items'):
                items = invoice.get('line_items', [])
                if items:
                    descriptions = [item.get('description', '') for item in items[:3]]
                    line_items_desc = ", ".join(descriptions)
                    if len(items) > 3:
                        line_items_desc += f" (and {len(items) - 3} more)"
        
            lines.append(f"| {vendor} | {date} | {amount:.2f} | {tax:.2f} | {currency} | {line_items_desc} |")
    
        lines.append("")
        lines.append("**TOTALS BY CURRENCY:**")
    
        for currency, total in totals_by_currency.items():
            tax_total = tax_by_currency[currency]
            lines.append(f"\n**{currency}:**")
            lines.append(f"- Total Amount (including tax): {total:.2f}")
            lines.append(f"- Total Tax: {tax_total:.2f}")
    
        return "\n".join(lines)
