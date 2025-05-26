# pdf_reporter.py

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

class PDFReporter:
    def generate_pdf_report(processed_data, config, stats):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        import os
        
        # Створення директорії для звітів
        os.makedirs("output/reports", exist_ok=True)
        
        # Створення PDF документа
        doc = SimpleDocTemplate("output/reports/population_report.pdf", pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Додавання стилів
        title_style = styles['Title']
        heading_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Заголовок
        elements.append(Paragraph(f"Country population report", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Інформація про період
        elements.append(Paragraph(f"Ananlysis period: {config['start_year']}-{config['end_year']}", normal_style))
        elements.append(Paragraph(f"Country: {', '.join(config['countries'])}", normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Додавання статистики
        elements.append(Paragraph("Static indicators", heading_style))
        
        if isinstance(stats, dict):
            data = [["Indicator", "Value"]]
            for key, value in stats.items():
                if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                    formatted_key = key.replace('_', ' ').title()
                    data.append([formatted_key, str(value)])
            
            table = Table(data, colWidths=[10*cm, 5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        # Додавання графіків
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("Data visualization", heading_style))
        
        # Перевірка наявності графіків у директорії
        figures_dir = "output/figures"
        if os.path.exists(figures_dir):
            for filename in os.listdir(figures_dir):
                if filename.endswith(('.png', '.jpg')):
                    img_path = os.path.join(figures_dir, filename)
                    
                    # Форматування назви графіка
                    chart_name = filename.replace('.png', '').replace('_', ' ').title()
                    elements.append(Paragraph(f"{chart_name}", styles['Heading2']))
                    
                    # Додавання зображення з масштабуванням
                    img = Image(img_path)
                    img.drawHeight = 10*cm
                    img.drawWidth = 15*cm
                    elements.append(img)
                    elements.append(Spacer(1, 0.5*cm))
        
        # Побудова документа
        doc.build(elements)
        print(f"PDF звіт згенеровано: output/reports/population_report.pdf")