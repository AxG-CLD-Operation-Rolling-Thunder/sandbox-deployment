EMAIL_GENERATION_PROMPT = """Compose a professional expense report email based on the following invoice data.

Invoice Summary:
{invoice_summary}

Additional Context: {additional_context}

Requirements for the email:
1. Start DIRECTLY with the email greeting (e.g., "Dear [Recipient's name],")
2. DO NOT include any introductory text about being a business expert or explaining what you're doing
3. DO NOT repeat the subject line in the email body
4. Clearly state the purpose (submitting expense report for reimbursement)
5. Include a summary table of all expenses with EXACTLY these columns:
   - Vendor_name
   - Invoice_date
   - Total_amount
   - Tax_amount (shown separately)
   - Currency
   - LineItems (brief description of items)
6. Format the table clearly with proper alignment
7. After the table, show currency totals that INCLUDE tax (add Total_amount + Tax_amount)
8. Format currency totals as: "TOTAL (USD): $X,XXX.XX (including tax)"
9. Mention that original receipts and invoices are available upon request
10. Include any relevant notes about the expenses
11. End with a professional closing

IMPORTANT: 
- Output ONLY the email body text, starting with the greeting
- Currency totals at the bottom MUST include tax (base + tax)
- DO NOT mention any attachments
- The table format must match the expense summary exactly

The email should be concise yet comprehensive, suitable for corporate expense reimbursement."""
