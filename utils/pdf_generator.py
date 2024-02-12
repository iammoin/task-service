import json
from config.logger import logger
# from fpdf import FPDF
# import pandas as pd
 
# def generate(data: dict, filename: str):
#     pdf = FPDF() 
#     pdf.add_page()
#     pdf.set_font('Arial', 'B', 16)
    
#     pdf.cell(0, 10, 'Tasks List', 0, 1)
#     pdf.set_font('Arial', '', 12)
#     df = pd.DataFrame(data)
#     df = df['personal_tasks', 'shared_tasks']
    
#     col_width = pdf.w / 2.2
#     row_height = pdf.font_size * 2
#     for issue in df.itertuples(index=False):
#         data = [
#             ['personal_tasks:', issue.personal_tasks],
#             ['shared_tasks:', issue.shared_tasks],
#         ]

#     # Draw table
#     for row in data:
#         pdf.multi_cell(col_width, row_height, str(row[0]), border=0)
#         pdf.multi_cell(col_width, row_height, str(row[1]), border=0)
#         pdf.ln(row_height)

#     # Draw line between tables
#     pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
#     pdf.ln(row_height)
#     pdf.output(f'{filename}', 'F')


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from io import BytesIO
import json
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def json_to_pdf(json_data, output_file='files/output.pdf'):
    # Create a BytesIO buffer to store the PDF content
    buffer = BytesIO()
    formatted_json = json.dumps(json_data, indent=4, default=str)
    
    text_width=A5[0] / 2
    text_height=A5[1] / 2
    x = A5[0]/4
    y = A5[1]/4
    # Create a PDF document using ReportLab
    pdf = canvas.Canvas(buffer, pagesize=A5)
    
    i=0
    batch=1500
    logger.info(msg=f"len json data ={len(formatted_json)}")
    while i<len(formatted_json):
        logger.info(msg=f"i={i}")
        styles = getSampleStyleSheet()
        p = Paragraph(formatted_json[i:i+batch], styles["Normal"])
        p.wrapOn(pdf, text_width, text_height)
        p.drawOn(pdf, x, y)
        i += batch
        pdf.showPage()
    pdf.save()
    buffer.seek(0)
    
    # Write the buffer content to the output file
    with open(output_file, 'wb') as output:
        output.write(buffer.read())

if __name__ == "__main__":
    # Example JSON data
    example_json_data = {
        "name": "John Doe",
        "age": 30,
        "city": "New York",
        "interests": ["programming", "reading", "traveling"]
    }

    # Convert JSON to PDF
    json_to_pdf(example_json_data, output_file='files/output.pdf')
