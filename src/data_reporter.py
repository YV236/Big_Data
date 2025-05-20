# pdf_reporter.py

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

class PDFReporter:
    def generate_interactive_pdf(processed_data, config):
        try:
            from borb.pdf import Document
            from borb.pdf import Page
            from borb.pdf import PDF
            from borb.pdf import SingleColumnLayout
            from borb.pdf.canvas.layout.image.image import Image as BorbImage
            from borb.pdf.canvas.layout.text.paragraph import Paragraph
            from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
            from borb.pdf.canvas.layout.table.table import TableCell
            from borb.pdf.canvas.color.color import HexColor
            from decimal import Decimal
            import os
        
            # Створення директорії для звітів
            os.makedirs("output/reports", exist_ok=True)
            
            # Створення документа
            doc = Document()
            page = Page()
            doc.add_page(page)
            layout = SingleColumnLayout(page)
            
            # Заголовок
            layout.add(Paragraph(f"Звіт про населення країн", 
                                font="Helvetica-Bold", 
                                font_size=Decimal(20)))
            
            # Інформація про період
            layout.add(Paragraph(f"Період аналізу: {config['start_year']}-{config['end_year']}", 
                                font="Helvetica", 
                                font_size=Decimal(12)))
            layout.add(Paragraph(f"Країни: {', '.join(config['countries'])}", 
                                font="Helvetica", 
                                font_size=Decimal(12)))
            
            # Додавання графіків
            layout.add(Paragraph("Візуалізація даних", 
                                font="Helvetica-Bold", 
                                font_size=Decimal(16)))
            
            # Перевірка наявності графіків
            figures_dir = "output/figures"
            if os.path.exists(figures_dir):
                for filename in os.listdir(figures_dir):
                    if filename.endswith(('.png', '.jpg')):
                        img_path = os.path.join(figures_dir, filename)
                        
                        # Назва графіка
                        chart_name = filename.replace('.png', '').replace('_', ' ').title()
                        layout.add(Paragraph(chart_name, 
                                            font="Helvetica-Bold", 
                                            font_size=Decimal(14)))
                        
                        # Додавання зображення
                        layout.add(BorbImage(img_path, width=Decimal(400)))
            
            # Збереження PDF
            pdf_path = "output/reports/population_interactive_report.pdf"
            with open(pdf_path, "wb") as pdf_file_handle:
                PDF.dumps(pdf_file_handle, doc)
            
            print(f"Інтерактивний PDF звіт згенеровано: {pdf_path}")
        except ImportError:
            print("Для використання Borb встановіть: pip install borb")


    def generate_simple_pdf_report(processed_data, config, stats):
        from fpdf import FPDF
        import os
        
        # Створення директорії для звітів
        os.makedirs("output/reports", exist_ok=True)
        
        # Створення PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Налаштування шрифтів
        pdf.set_font("Arial", "B", 16)
        
        # Заголовок
        pdf.cell(0, 10, "Звіт про населення країн", ln=True, align="C")
        pdf.ln(5)
        
        # Інформація про період
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Період аналізу: {config['start_year']}-{config['end_year']}", ln=True)
        pdf.cell(0, 10, f"Країни: {', '.join(config['countries'])}", ln=True)
        pdf.ln(5)
        
        # Статистика
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Статистичні показники", ln=True)
        pdf.set_font("Arial", "", 12)
        
        if isinstance(stats, dict):
            for key, value in stats.items():
                if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                    formatted_key = key.replace('_', ' ').title()
                    pdf.cell(0, 10, f"{formatted_key}: {value}", ln=True)
        
        # Додавання графіків
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Візуалізація даних", ln=True)
        
        # Перевірка наявності графіків
        figures_dir = "output/figures"
        if os.path.exists(figures_dir):
            for filename in os.listdir(figures_dir):
                if filename.endswith(('.png', '.jpg')):
                    img_path = os.path.join(figures_dir, filename)
                    
                    # Назва графіка
                    chart_name = filename.replace('.png', '').replace('_', ' ').title()
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, chart_name, ln=True)
                    
                    # Додавання зображення
                    pdf.image(img_path, x=10, y=None, w=190)
                    pdf.ln(5)
        
        # Збереження PDF
        pdf_path = "output/reports/population_simple_report.pdf"
        pdf.output(pdf_path)
        print(f"Простий PDF звіт згенеровано: {pdf_path}")

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
        elements.append(Paragraph(f"Звіт про населення країн", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Інформація про період
        elements.append(Paragraph(f"Період аналізу: {config['start_year']}-{config['end_year']}", normal_style))
        elements.append(Paragraph(f"Країни: {', '.join(config['countries'])}", normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Додавання статистики
        elements.append(Paragraph("Статистичні показники", heading_style))
        
        if isinstance(stats, dict):
            data = [["Показник", "Значення"]]
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
        elements.append(Paragraph("Візуалізація даних", heading_style))
        
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