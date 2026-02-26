from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_ticket_pdf(booking):
    directory = "tickets"
    file_name = f"tickets/{booking['ticket_no']}.pdf"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

    c = canvas.Canvas(file_name)

    c.drawString(100, 800, "Travello Bus Ticket")
    c.drawString(100, 770, f"Ticket No: {booking['ticket_no']}")
    c.drawString(100, 740, f"User: {booking['user_id']}")
    c.drawString(100, 710, f"Trip: {booking['trip_id']}")
    c.drawString(100, 680, f"Seats: {', '.join(booking['seats'])}")
    c.drawString(100, 650, f"Amount: {booking['total_price']}")
    c.drawString(100, 620, f"Date: {datetime.now()}")

    c.save()

    return file_name