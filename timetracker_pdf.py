from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Frame, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import PageBreak
from reportlab.platypus import FrameBreak
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from datetime import datetime
import json
import sys
import os

# Hour rate
try:
    hour_rate = float(input("Please enter the hourly rate: "))
except ValueError:
    print("That's not a valid hourly rate. Please enter a number.")
    # You can then either exit the program or ask the user to enter the hourly rate again

# Load data from .timetracker file
with open('.timetracker', 'r') as f:
    data = json.load(f)

# Check if we're running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # We're running in a PyInstaller bundle
    ttf_path = os.path.join(sys._MEIPASS, 'Roboto-Regular.ttf')
else:
    # We're running in a normal Python environment
    ttf_path = 'Roboto-Regular.ttf'

# Register the Roboto font
pdfmetrics.registerFont(TTFont('Roboto', ttf_path))

# Create a new style based on the 'Normal' style
styles = getSampleStyleSheet()
header_style = ParagraphStyle('Roboto', parent=styles['Normal'], fontName='Roboto', fontSize=28)
footer_style = ParagraphStyle('Roboto', parent=styles['Normal'], fontName='Roboto', fontSize=11)

# Create document
now = datetime.now()
date_string = now.strftime("%Y%m%d%H%M%S")
filename = "invoice_{}.pdf".format(date_string)
doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)

def on_first_page(canvas, doc):
    # Save the state of our canvas so we can draw on it
    canvas.saveState()

    # Header
    header_text = 'ΣΗΜΕΙΩΜΑ ΧΡΕΩΣΗΣ'
    header = Paragraph(header_text, header_style)
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.width - w + 150.0, doc.height + doc.topMargin - h + 32.0)

    # Footer
    footer_text = 'Ελάχιστη χρέωση 30 λεπτα'
    footer = Paragraph(footer_text, footer_style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.width - 50, h)

	# Page number
    page_number = Paragraph(str(canvas.getPageNumber()), footer_style)
    w, h = page_number.wrap(doc.width, doc.bottomMargin)
    page_number.drawOn(canvas, doc.width - 150, h)

    # Release the canvas
    canvas.restoreState()

def on_other_pages(canvas, doc):
    # Save the state of our canvas so we can draw on it
    canvas.saveState()

    # Footer
    footer_text = 'Ελάχιστη χρέωση 30 λεπτα'
    footer = Paragraph(footer_text, footer_style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.width - 50, h)

    # Page number
    page_number = Paragraph(str(canvas.getPageNumber()), footer_style)
    w, h = page_number.wrap(doc.width, doc.bottomMargin)
    page_number.drawOn(canvas, doc.width - 150, h)

    # Release the canvas
    canvas.restoreState()

# Build the document using the on_first_page and on_other_pages functions
doc.build([], onFirstPage=on_first_page, onLaterPages=on_other_pages)

	# Create frames for the first and other pages
frame_first_page = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame_first_page')
frame_other_pages = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame_other_pages')

# Create page templates for the first and other pages
template_first_page = PageTemplate(id='FirstPage', frames=frame_first_page, onPage=on_first_page)
template_other_pages = PageTemplate(id='OtherPages', frames=frame_other_pages, onPage=on_other_pages)

# Set the page templates
doc.addPageTemplates([template_first_page, template_other_pages])

# Create table data
table_data = [["Έναρξη", "Λήξη", "Διάρκεια (sec)", "Διάρκεια (min)"]]

total_seconds = 0
total_minutes = 0

for session in data['sessions']:
    begin = datetime.strptime(session['begin'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d-%m-%Y %H:%M:%S')
    end = datetime.strptime(session['end'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d-%m-%Y %H:%M:%S')
    duration_seconds = session['duration']
    duration_minutes = round(duration_seconds / 60, 2)
    table_data.append([begin, end, duration_seconds, "{:.2f}".format(duration_minutes)])

    # Add to totals
    total_seconds += duration_seconds
    total_minutes += duration_minutes

# Append totals to table_data
table_data.append(['', '', '', ''])
table_data.append(['Σύνολο', '', total_seconds, "{:.2f}".format(total_minutes)])
cost = (total_minutes / 60) * hour_rate
hours = total_minutes // 60
remaining_minutes = total_minutes % 60
table_data.append(['Κόστος', "{} ώρες {} λεπτά * {} €/ώρα".format(int(hours), int(remaining_minutes), hour_rate), '', "{:.2f} €".format(cost)])

# Create table
table = Table(table_data)

	# Add table style
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),

    ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),

    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
	('SPAN', (1, -1), (2, -1))  # Span from 2nd to 3rd column of last row
]))

# Add the table to the story
story = [table]

# Build the document with the story
doc.build(story)