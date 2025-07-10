from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import os

def generate_quotation_pdf(quotation_data):
    """Generate a professional quotation PDF"""
    
    # Create a buffer to hold the PDF
    buffer = BytesIO()
    
    # Create the PDF document with reduced margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563EB'),
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#1E293B')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#1E293B')
    )
    
    # Header Section - Company info aligned to top-right
    header_company_info = f"""
    <para align="right">
    <b>{quotation_data['company']['name']}</b><br/>
    {quotation_data['company']['address']}<br/>
    Email: {quotation_data['company']['email']}<br/>
    Contact: {quotation_data['company']['phone']}<br/>
    GST: {quotation_data['company']['gst']}<br/>
    MSME: {quotation_data['company']['msme']}
    </para>
    """
    
    # Logo handling - check if logo exists in session state
    logo_element = "[LOGO PLACEHOLDER]"
    if 'company_logo' in quotation_data and quotation_data['company_logo']:
        try:
            # If logo data is available, create an Image element from BytesIO
            logo_buffer = BytesIO(quotation_data['company_logo'].getvalue())
            logo_element = Image(logo_buffer, width=1.5*inch, height=1*inch)
        except Exception as e:
            logo_element = "[LOGO]"
    
    # Header table with logo, blank center, company info
    header_data = [
        [logo_element, "", Paragraph(header_company_info, normal_style)]
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 2*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # Title - centered and bold
    title = Paragraph("<b>QUOTATION</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Party & Quote Details Section
    client_info = f"""
    <b>To:</b><br/>
    {quotation_data['client']['name']}<br/>
    {quotation_data['client']['address']}<br/>
    Email: {quotation_data['client']['email']}<br/>
    Contact: {quotation_data['client']['phone']}<br/>
    Attn: {quotation_data['client']['contact_person']}
    """
    
    quote_details = f"""
    <para align="right">
    <b>Quotation No:</b> {quotation_data['quote_ref']}<br/>
    <b>Date:</b> {quotation_data['quote_date']}<br/>
    <b>Valid Till:</b> {quotation_data['validity_date']}<br/>
    </para>
    """
    
    # Party and quote details table
    party_quote_data = [
        [Paragraph(client_info, normal_style), "", Paragraph(quote_details, normal_style)]
    ]
    
    party_quote_table = Table(party_quote_data, colWidths=[3*inch, 1*inch, 3*inch])
    party_quote_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(party_quote_table)
    elements.append(Spacer(1, 20))
    
    # Subject
    if quotation_data.get('subject'):
        subject_para = Paragraph(f"<b>SUB:</b> {quotation_data['subject']}", normal_style)
        elements.append(subject_para)
        elements.append(Spacer(1, 12))
    
    # Introductory Note - left aligned
    greeting = Paragraph("Dear Sir/Madam,<br/><br/>We thank you for your interest shown in our products. We are hereby quoting for your requirements.", normal_style)
    elements.append(greeting)
    elements.append(Spacer(1, 20))
    
    # Line Items Table with updated structure and better formatting
    # Create wrapped headers to prevent overflow
    header_style_wrapped = ParagraphStyle(
        'HeaderWrapped',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.whitesmoke,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    line_items_data = [
        [
            Paragraph('Sr.', header_style_wrapped),
            Paragraph('Item Description', header_style_wrapped),
            Paragraph('HSN/SAC Code', header_style_wrapped),
            Paragraph('Quantity/UOM', header_style_wrapped),
            Paragraph('Rate', header_style_wrapped),
            Paragraph('Discount', header_style_wrapped),
            Paragraph('Total', header_style_wrapped)
        ]
    ]
    
    for idx, item in enumerate(quotation_data['line_items'], 1):
        # Combine part_no and description
        item_description = f"{item['part_no']}\n{item['description']}"
        if item.get('delivery_weeks'):
            item_description += f"\nDelivery: {item['delivery_weeks']} weeks"
        
        # Format quantity with proper UOM
        qty_formatted = f"{item['qty']} No" if item['qty'] == 1 else f"{item['qty']} Nos"
        
        # Get item discount from data
        item_discount = item.get('discount_percent', 0)
        
        line_items_data.append([
            str(idx),
            item_description,
            item['hsn'],
            qty_formatted,
            f"{item['unit_price']:,.2f}",
            f"{item_discount:,.1f}%" if item_discount > 0 else "0",
            f"{item['total_price']:,.2f}"
        ])
    
    # Add discount row if applicable
    if quotation_data['totals']['discount_amount'] > 0:
        line_items_data.append(['', '', '', '', '', 'Discount:', f"-{quotation_data['totals']['discount_amount']:,.2f}"])
    
    # Add GST row
    line_items_data.append(['', '', '', '', '', 'GST (18%):', f"{quotation_data['totals']['gst_amount']:,.2f}"])
    
    # Add total row
    line_items_data.append(['', '', '', '', '', 'Total Amount:', f"{quotation_data['totals']['total_amount']:,.2f}"])
    
    line_items_table = Table(line_items_data, colWidths=[0.4*inch, 2.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch], repeatRows=1)
    line_items_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows styling - remove background color
        ('ALIGN', (0, 1), (0, -4), 'CENTER'),  # Sr. number center
        ('ALIGN', (1, 1), (1, -4), 'LEFT'),    # Item description left
        ('ALIGN', (2, 1), (2, -4), 'CENTER'),  # HSN center
        ('ALIGN', (3, 1), (3, -4), 'RIGHT'),   # Quantity right
        ('ALIGN', (4, 1), (4, -4), 'RIGHT'),   # Rate right
        ('ALIGN', (5, 1), (5, -4), 'RIGHT'),   # Discount right
        ('ALIGN', (6, 1), (6, -4), 'RIGHT'),   # Total right
        
        # Summary rows styling
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#F8FAFC')),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (5, -3), (5, -1), 'RIGHT'),   # Summary labels right
        ('ALIGN', (6, -3), (6, -1), 'RIGHT'),   # Summary values right
        
        # General styling
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    
    elements.append(line_items_table)
    elements.append(Spacer(1, 20))
    
    # Terms and Conditions
    terms_header = Paragraph("Terms & Conditions", header_style)
    elements.append(terms_header)
    
    terms_text = f"""
    <b>Payment:</b> {quotation_data['terms']['payment']}<br/>
    <b>Price:</b> {quotation_data['terms']['price']}<br/>
    <b>Freight & Transit Insurance:</b> {quotation_data['terms']['freight']}<br/>
    <b>Additional Terms:</b> {quotation_data['terms']['additional']}<br/>
    <b>Offer Validity:</b> {quotation_data['validity_date']}<br/>
    <br/>
    <b>Warranty:</b> {quotation_data['terms']['warranty']}<br/>
    <b>Cancellation:</b> {quotation_data['terms']['cancellation']}<br/>
    <b>Penalty:</b> {quotation_data['terms']['penalty']}<br/>
    """
    
    terms_para = Paragraph(terms_text, normal_style)
    elements.append(terms_para)
    elements.append(Spacer(1, 20))
    
    # Footer - Better formatted signature block
    footer_text = f"""
    We hope you find our offer in line with your requirement; however, any queries feel free to contact us.
    """
    
    signature_text = f"""
    <para align="left">
    Cordially yours,<br/>
    <br/>
    <b>{quotation_data['company']['name']}</b><br/>
    Contact: {quotation_data['company']['phone']}<br/>
    Email: {quotation_data['company']['email']}
    </para>
    """
    
    footer_para = Paragraph(footer_text, normal_style)
    elements.append(footer_para)
    elements.append(Spacer(1, 12))
    
    signature_para = Paragraph(signature_text, normal_style)
    elements.append(signature_para)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data
