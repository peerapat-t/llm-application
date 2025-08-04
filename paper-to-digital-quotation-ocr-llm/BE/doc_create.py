import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

FONT_PATH = './FONT/NotoSansThai-VariableFont_wdth,wght.ttf'
if not os.path.exists(FONT_PATH):
    print(f"ไม่พบไฟล์ฟอนต์ '{FONT_PATH}'")
    exit()
pdfmetrics.registerFont(TTFont('NotoSansThai', FONT_PATH))

QUOTE_DETAIL = {"date": ""}
CURRENT_DATE = datetime.today().strftime('%Y-%m-%d')
QUOTE_DETAIL['date'] = CURRENT_DATE

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ThaiNormal', fontName='NotoSansThai', fontSize=11, leading=14))
styles.add(ParagraphStyle(name='ThaiBold', fontName='NotoSansThai', fontSize=11, leading=14))
styles.add(ParagraphStyle(name='ThaiH1', fontName='NotoSansThai', fontSize=18, leading=22))

COMPANY_INFO = {
    "name": "บริษัท สมาร์ทเทค จำกัด",
    "address": "123 ถนนสุขุมวิท กรุงเทพฯ 10110",
    "email": "somchai@smarttech.co.th",
    "telephone_number": "02-123-4567"
}

def create_quotation(file_path, customer_info, items):
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    story = []

    story.append(Paragraph("<b>ใบเสนอราคา / Quotation</b>", styles['ThaiH1']))
    story.append(Spacer(1, 0.2 * inch))

    company_text = f"""<b>จาก:</b><br/>{COMPANY_INFO['name']}<br/>{COMPANY_INFO['address']}<br/>อีเมล: {COMPANY_INFO['email']}<br/>โทร: {COMPANY_INFO['telephone_number']}"""
    customer_text = f"""<b>ถึง:</b><br/>{customer_info['name']}<br/>{customer_info['address']}<br/>อีเมล: {customer_info['email']}<br/>โทร: {customer_info['telephone_number']}"""

    company_customer_data = [[Paragraph(company_text, styles['ThaiNormal']), Paragraph(customer_text, styles['ThaiNormal'])]]
    company_customer_table = Table(company_customer_data, colWidths=[3.5 * inch, 3.5 * inch])
    company_customer_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(company_customer_table)
    story.append(Spacer(1, 0.2 * inch))

    quote_details_data = [[Paragraph(f"", styles['ThaiNormal']), Paragraph(f"วันที่: {QUOTE_DETAIL['date']}", styles['ThaiNormal'])]]
    quote_details_table = Table(quote_details_data, colWidths=[3.5 * inch, 3.5 * inch])
    story.append(quote_details_table)
    story.append(Spacer(1, 0.3 * inch))

    header = [Paragraph(f"<b>{h}</b>", styles['ThaiNormal']) for h in ["ลำดับ", "รายการ", "จำนวน", "ราคา/หน่วย", "รวม"]]
    
    item_paragraphs = []
    for row in items:
        formatted_row = [
            Paragraph(str(row[0]), styles['ThaiNormal']),
            Paragraph(row[1], styles['ThaiNormal']),
            Paragraph(f"{row[2]:,}", styles['ThaiNormal']),
            Paragraph(f"{row[3]:,.2f}", styles['ThaiNormal']),
            Paragraph(f"{row[4]:,.2f}", styles['ThaiNormal'])
        ]
        item_paragraphs.append(formatted_row)

    table_data = [header] + item_paragraphs

    item_table = Table(table_data, colWidths=[0.8 * inch, 3.2 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4A4A4A")), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black), ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 0.2 * inch))

    subtotal = sum(item[4] for item in items)
    vat = subtotal * 0.06
    total = subtotal + vat

    summary_data = [
        [Paragraph("ยอดรวม (Subtotal):", styles['ThaiNormal']), Paragraph(f"{subtotal:,.2f} บาท", styles['ThaiNormal'])],
        [Paragraph("ภาษีมูลค่าเพิ่ม (VAT 7%):", styles['ThaiNormal']), Paragraph(f"{vat:,.2f} บาท", styles['ThaiNormal'])],
        [Paragraph("<b>ยอดรวมทั้งสิ้น (Total):</b>", styles['ThaiBold']), Paragraph(f"<b>{total:,.2f} บาท</b>", styles['ThaiBold'])],
    ]
    summary_table = Table(summary_data, colWidths=[5 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT')]))
    story.append(summary_table)
    story.append(Spacer(1, 1 * inch))

    signature_data = [
        [Paragraph("<b>ผู้มีอำนาจลงนาม</b>", styles['ThaiNormal'])],
        [Spacer(1, 0.3 * inch)],
        [Paragraph("________________________", styles['ThaiNormal'])],
        [Paragraph("(สมชาย รักเรียน)", styles['ThaiNormal'])],
    ]
    signature_table = Table(signature_data, colWidths=[5 * inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(signature_table)
    doc.build(story)