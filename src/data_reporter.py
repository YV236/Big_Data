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
        
        # Creating directory for reports
        os.makedirs("output/reports", exist_ok=True)
        
        # Creating PDF document
        doc = SimpleDocTemplate("output/reports/population_report.pdf", pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Adding styles
        title_style = styles['Title']
        heading_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph(f"Country population report", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Information about the period
        elements.append(Paragraph(f"Analysis period: {config['start_year']}-{config['end_year']}", normal_style))
        elements.append(Paragraph(f"Countries: {', '.join(config['countries'])}", normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Adding statistics
        elements.append(Paragraph("Statistical indicators", heading_style))
        
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
        
        # Adding charts
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("Data visualization", heading_style))
        
        # Checking for charts in the directory
        figures_dir = "output/figures"
        if os.path.exists(figures_dir):
            for filename in os.listdir(figures_dir):
                if filename.endswith(('.png', '.jpg')):
                    img_path = os.path.join(figures_dir, filename)
                    
                    # Formatting chart name
                    chart_name = filename.replace('.png', '').replace('_', ' ').title()
                    elements.append(Paragraph(f"{chart_name}", styles['Heading2']))
                    
                    # Adding image with scaling
                    img = Image(img_path)
                    img.drawHeight = 10*cm
                    img.drawWidth = 15*cm
                    elements.append(img)
                    elements.append(Spacer(1, 0.5*cm))
        
        #  Building document
        doc.build(elements)
        print(f"PDF report generated: output/reports/population_report.pdf")