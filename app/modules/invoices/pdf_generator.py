from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from decimal import Decimal
from typing import Any, Dict

def generate_invoice_pdf(invoice_data: Dict[str, Any], tenant_data: Dict[str, Any], customer_data: Dict[str, Any]) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    header_style = styles['Normal']
    
    # 1. Header (Clinic/Workshop Info)
    elements.append(Paragraph(f"<b>{tenant_data.get('name', 'EKA WORKSHOP')}</b>", title_style))
    elements.append(Paragraph(f"GSTIN: {tenant_data.get('gst_number', 'N/A')}", header_style))
    elements.append(Paragraph(f"Address: {tenant_data.get('city', '')}, {tenant_data.get('state', '')}", header_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 2. Bill To
    elements.append(Paragraph("<b>BILL TO:</b>", styles['Heading3']))
    elements.append(Paragraph(f"Customer: {customer_data.get('name', 'Valued Customer')}", header_style))
    elements.append(Paragraph(f"Vehicle: {customer_data.get('plate_number', 'N/A')} ({customer_data.get('make', '')} {customer_data.get('model', '')})", header_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 3. Invoice Meta
    elements.append(Paragraph(f"Invoice ID: INV-{invoice_data.get('id')}", header_style))
    elements.append(Paragraph(f"Date: {invoice_data.get('created_at', '')}", header_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # 4. Table Data
    data = [['Description', 'Qty', 'Rate', 'GST%', 'Amount']]
    for line in invoice_data.get('lines', []):
        gst_pct = line.get('tax_rate', 18)
        taxable = line.get('price', 0) * line.get('quantity', 1)
        data.append([
            line.get('description', 'Item'),
            str(line.get('quantity', 1)),
            f"{line.get('price', 0):,.2f}",
            f"{gst_pct}%",
            f"{taxable:,.2f}"
        ])
    
    table = Table(data, colWidths=[2.5*inch, 0.5*inch, 1*inch, 0.8*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 5. Totals
    total_taxable = sum(l.get('price', 0) * l.get('quantity', 1) for l in invoice_data.get('lines', []))
    tax_amt = invoice_data.get('tax_amount', 0)
    total_amt = invoice_data.get('total_amount', 0)
    
    totals_data = [
        ['Total Taxable', f"INR {total_taxable:,.2f}"],
        ['Total Tax (GST)', f"INR {tax_amt:,.2f}"],
        ['Grand Total', f"INR {total_amt:,.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch], hAlign='RIGHT')
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),
    ]))
    elements.append(totals_table)
    
    # Build
    doc.build(elements)
    buffer.seek(0)
    return buffer
