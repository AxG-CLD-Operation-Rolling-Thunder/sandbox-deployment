SUMMARY_GENERATION_PROMPT = """You are a data formatting assistant. Your task is to take raw invoice data and present it in a clear, well-structured table for a report.

Number of invoices: {invoice_count}
Raw invoice data:
{invoices_json}

Format the data into a single table with the following specific columns:
- Vendor_name
- Invoice_date
- Total_amount
- Tax_amount
- Currency
- LineItems (a brief summary of the items/services)

After the table, provide a separate section with the calculated totals for each currency.
IMPORTANT: Currency totals should include tax amounts (Total_amount + Tax_amount).

Ensure all amounts are formatted to two decimal places and the table is properly aligned for readability."""
