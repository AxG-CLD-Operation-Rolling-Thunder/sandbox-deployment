"""
Email Drafting Tool for composing and creating Gmail drafts
Uses Gemini 2.5 Pro for professional email composition
"""

import os
import json
import base64
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from invoice_agent.prompts import email_generation_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_CONFIG = {
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048
}

class EmailComposer:
    """Main class for composing expense report emails and creating Gmail drafts"""
    
    def __init__(self, api_key: str):
        """
        Initialize the email composer with Gemini API
        
        Args:
            api_key: Google AI API key for Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def _create_fallback_email_body(
    self,
    invoice_data: List[Dict[str, Any]],
    additional_context: Optional[str] = None
) -> str:
        """Create a template-based email body as fallback with consistent format"""
        totals_by_currency = {}
        tax_totals_by_currency = {}
    
        for invoice in invoice_data:
            currency = invoice.get('currency', 'USD')
            amount = invoice.get('total_amount', 0)
            tax = invoice.get('tax_amount', 0)
        
            if currency not in totals_by_currency:
                totals_by_currency[currency] = 0
                tax_totals_by_currency[currency] = 0
        
            totals_by_currency[currency] += amount
            tax_totals_by_currency[currency] += tax
    
        expense_lines = []
        expense_lines.append("EXPENSE SUMMARY")
        expense_lines.append("=" * 100)
        expense_lines.append(
        f"{'Vendor_name':<25} {'Invoice_date':<15} {'Total_amount':<15} "
        f"{'Tax_amount':<12} {'Currency':<10} {'LineItems':<30}"
        )
        expense_lines.append("-" * 100)
    
        for invoice in invoice_data:
            vendor = invoice.get('vendor_name', 'Unknown')[:25]
            date = invoice.get('invoice_date', 'N/A')
            amount = invoice.get('total_amount', 0)  # Base amount without tax
            tax = invoice.get('tax_amount', 0)
            currency = invoice.get('currency', 'USD')
        
            line_items_desc = "General expense"
            if invoice.get('line_items'):
                items = [item.get('description', '') for item in invoice['line_items'][:2]]
                line_items_desc = ", ".join(items)[:30]
                if len(invoice['line_items']) > 2:
                    line_items_desc += "..."
        
            expense_lines.append(
            f"{vendor:<25} {date:<15} {amount:<15.2f} "
            f"{tax:<12.2f} {currency:<10} {line_items_desc:<30}"
            )
    
        expense_lines.append("-" * 100)
    
        for currency in totals_by_currency:
            base_total = totals_by_currency[currency]
            tax_total = tax_totals_by_currency[currency]
            grand_total = base_total + tax_total
        
            expense_lines.append(
            f"{'TOTAL (' + currency + ')':<25} {'':<15} "
            f"{grand_total:<15.2f} {'':<12} {currency:<10} {'(including tax)':<30}"
        )
    
        expense_table = "\n".join(expense_lines)
    
        email_body = f"""Dear [Recipient's name],

I am submitting my expense report for reimbursement. Please find the details below:

{expense_table}

{f"Additional Notes: {additional_context}" if additional_context else ""}

All original receipts and invoices are available upon request. Please let me know if you need any additional information or documentation.

Thank you for processing this expense report.

Best regards"""
    
        return email_body
    
    def create_expense_email_draft(
        self,
        invoice_data: List[Dict[str, Any]],
        credentials: Union[Credentials, str],
        recipient_email: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Gmail draft with expense report based on invoice data
        
        Args:
            invoice_data: List of validated invoice dictionaries
            credentials: Either OAuth 2.0 Credentials object or access token string
            recipient_email: Optional recipient (defaults to authorized user's email)
            cc_emails: Optional list of CC recipients
            additional_context: Optional context or notes to include
            
        Returns:
            Dictionary containing draft ID and status
        """
        try:
            logger.info("Building Gmail service with user credentials")
            service = self._build_gmail_service(credentials)
            
            if not recipient_email:
                try:
                    profile = service.users().getProfile(userId='me').execute()
                    recipient_email = profile.get('emailAddress')
                    logger.info(f"Using authorized user's email as recipient: {recipient_email}")
                except Exception as e:
                    logger.warning(f"Could not get user email, using 'me' as recipient: {e}")
                    recipient_email = 'me'
            
            logger.info("Composing email body with Gemini Pro")
            email_content = self._compose_email_body(invoice_data, additional_context)
            
            subject = self._generate_subject(invoice_data)
            
            logger.info("Creating MIME message")
            message = self._create_mime_message(
                recipient_email,
                subject,
                email_content,
                cc_emails
            )
            
            logger.info("Creating draft in user's Gmail account")
            draft_id = self._create_gmail_draft(service, message)
            
            logger.info(f"Successfully created Gmail draft with ID: {draft_id}")
            
            return {
                "success": True,
                "draft_id": draft_id,
                "message": "Email draft created successfully in your Gmail account",
                "subject": subject,
                "recipient": recipient_email
            }
            
        except HttpError as error:
            error_details = error.error_details if hasattr(error, 'error_details') else str(error)
            logger.error(f"Gmail API error: {error_details}")
            
            if error.resp.status in [401, 403]:
                return {
                    "success": False,
                    "error": "Authentication failed. Please re-authorize Gmail access.",
                    "error_code": error.resp.status,
                    "message": "Gmail authorization expired or insufficient permissions"
                }
            else:
                return {
                    "success": False,
                    "error": f"Gmail API error: {error_details}",
                    "message": "Failed to create email draft"
                }
                
        except Exception as e:
            logger.error(f"Failed to create email draft: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create email draft"
            }
    
    def _compose_email_body(
        self,
        invoice_data: List[Dict[str, Any]],
        additional_context: Optional[str] = None
    ) -> str:
        """Generate professional email body using Gemini Pro"""
        
        logger.info(f"Number of invoices: {len(invoice_data)}")
        logger.info(f"First invoice keys: {list(invoice_data[0].keys()) if invoice_data else 'No invoices'}")
        logger.info(f"First invoice sample: {json.dumps(invoice_data[0], indent=2) if invoice_data else 'No data'}")
    
        invoice_summary = self._format_invoice_summary(invoice_data)
        logger.info(f"Formatted summary length: {len(invoice_summary)}")
    
        prompt = email_generation_prompt.EMAIL_GENERATION_PROMPT.format(
            invoice_summary=invoice_summary,
            additional_context=additional_context if additional_context else "None provided"
        )
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.debug(f"Full prompt: {prompt[:500]}...")  # First 500 chars
        safety_settings = [
        {
            "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
            "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
        },
        {
            "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
        },
        {
            "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
        },
        {
            "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
        }
        ]
        try:
            response = self.model.generate_content(
            prompt,
            generation_config=EMAIL_CONFIG,
            safety_settings=safety_settings

                )
        
            if response.prompt_feedback:
                logger.warning(f"Prompt feedback: {response.prompt_feedback}")
        
            if response.parts:
                return response.text
            else:
                logger.warning("No parts in response, checking candidates")
                if response.candidates:
                    for candidate in response.candidates:
                        logger.warning(f"Candidate finish reason: {candidate.finish_reason}")
                        logger.warning(f"Candidate safety ratings: {candidate.safety_ratings}")
            
                return self._create_fallback_email_body(invoice_data, additional_context)
                
        except Exception as e:
            logger.error(f"Error generating email with Gemini: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            return self._create_fallback_email_body(invoice_data, additional_context)
    
    def _format_invoice_summary(self, invoice_data: List[Dict[str, Any]]) -> str:
        """Format invoice data into a summary string for the prompt"""
        summary_lines = []
        total_by_currency = {}
    
        for idx, invoice in enumerate(invoice_data, 1):
            vendor = str(invoice.get('vendor_name', 'Unknown Vendor')).strip()
            date = str(invoice.get('invoice_date', 'N/A')).strip()
            amount = float(invoice.get('total_amount', 0))
            tax_amount = float(invoice.get('tax_amount', 0))
            currency = str(invoice.get('currency', 'USD')).strip()
        
            vendor = vendor.replace('"', "'").replace('\n', ' ')
        
            if currency not in total_by_currency:
                total_by_currency[currency] = 0
            total_by_currency[currency] += (amount + tax_amount)
        
            items_desc = "General expense"
            if invoice.get('line_items'):
                items = [str(item.get('description', '')).strip() for item in invoice['line_items'][:3]]
                items_desc = ", ".join(items).replace('\n', ' ')
                if len(invoice['line_items']) > 3:
                    items_desc += f" (and {len(invoice['line_items']) - 3} more items)"
        
            summary_lines.append(
            f"Invoice {idx}: {vendor} | Date: {date} | "
            f"Amount: {currency} {amount:.2f} | Tax: {tax_amount:.2f} | Items: {items_desc}"
        )
    
        summary_lines.append("\nTotals by currency (including tax):")
        for currency, total in total_by_currency.items():
            summary_lines.append(f"  {currency}: {total:.2f}")
    
        return "\n".join(summary_lines)
    
    def _generate_subject(self, invoice_data: List[Dict[str, Any]]) -> str:
        """Generate email subject based on invoice data"""
        dates = [inv.get('invoice_date', '') for inv in invoice_data if inv.get('invoice_date')]
    
        if dates:
            dates.sort()
            start_date = datetime.strptime(dates[0], '%Y-%m-%d').strftime('%B %d')
            end_date = datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%B %d, %Y')
        
            if dates[0] == dates[-1]:
                date_range = end_date
            else:
                date_range = f"{start_date} - {end_date}"
        else:
            date_range = datetime.now().strftime('%B %Y')
    
        total_with_tax = sum(
        inv.get('total_amount', 0) + inv.get('tax_amount', 0) 
        for inv in invoice_data
        )
    
        return f"Expense Report - {date_range} (Total: ${total_with_tax:.2f})"
    
    def _build_gmail_service(self, credentials: Union[Credentials, str]):
        """Build Gmail API service with OAuth credentials"""
        
        if isinstance(credentials, str):
            credentials = Credentials(token=credentials)
        elif not isinstance(credentials, Credentials):
            raise ValueError("Credentials must be either a Credentials object or an access token string")
        
        try:
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            logger.info(f"Authenticated as: {profile.get('emailAddress')}")
            return service
        except HttpError as error:
            logger.error(f"Failed to build Gmail service: {error}")
            raise
    
    def _create_mime_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Create MIME message for Gmail API"""
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        
        if cc_emails:
            message['cc'] = ', '.join(cc_emails)
        
        message.attach(MIMEText(body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {'raw': raw_message}
    
    def _create_gmail_draft(self, service, message: Dict[str, str]) -> str:
        """Create draft in Gmail using the API"""
        try:
            draft = service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            logger.info(f"Draft created with ID: {draft['id']}")
            return draft['id']
            
        except HttpError as error:
            logger.error(f"An error occurred creating draft: {error}")
            raise


def create_expense_email_draft(
    invoice_data: List[Dict[str, Any]],
    credentials: Union[Credentials, str] = None,
    access_token: str = None,
    recipient_email: str = None,
    api_key: str = None,
    cc_emails: Optional[List[str]] = None,
    additional_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to create an expense report email draft
    
    Args:
        invoice_data: List of invoice data dictionaries
        credentials: OAuth 2.0 Credentials object (preferred)
        access_token: OAuth 2.0 access token string (for backward compatibility)
        recipient_email: Recipient email address
        api_key: Google AI API key
        cc_emails: Optional CC recipients
        additional_notes: Optional additional context
        
    Returns:
        Dictionary with draft creation results
    """
    if credentials is None and access_token is not None:
        credentials = access_token
    
    if credentials is None:
        raise ValueError("Either credentials or access_token must be provided")
    
    composer = EmailComposer(api_key)
    
    return composer.create_expense_email_draft(
        invoice_data=invoice_data,
        credentials=credentials,
        recipient_email=recipient_email,
        cc_emails=cc_emails,
        additional_context=additional_notes
    )
