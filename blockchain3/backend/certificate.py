import hashlib
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
from datetime import datetime

SERVER_IP = "192.168.31.171"
SERVER_PORT = "5000"


def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()


def generate_certificate(student, course, institution, hash_val):
    os.makedirs("certificates/pdf", exist_ok=True)
    os.makedirs("certificates/qr", exist_ok=True)

    pdf_path = f"certificates/pdf/{hash_val}.pdf"
    qr_path = f"certificates/qr/{hash_val}.png"

    # ---------------- PDF DESIGN ---------------- #
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Outer Border
    c.setStrokeColor(colors.HexColor("#1e3c72"))
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    # Inner Border
    c.setStrokeColor(colors.HexColor("#f59e0b"))
    c.setLineWidth(2)
    c.rect(45, 45, width - 90, height - 90)

    # Title
    c.setFont("Times-Bold", 28)
    c.setFillColor(colors.HexColor("#1e3c72"))
    c.drawCentredString(width / 2, height - 140, "CERTIFICATE")

    c.setFont("Times-Roman", 16)
    c.drawCentredString(width / 2, height - 175, "OF ACHIEVEMENT")

    # Body Text
    c.setFont("Times-Roman", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 240, "This is proudly presented to")

    # Student Name
    c.setFont("Times-Bold", 24)
    c.drawCentredString(width / 2, height - 290, student)

    # Course Text
    c.setFont("Times-Roman", 14)
    c.drawCentredString(width / 2, height - 340, "for successfully completing the course")

    c.setFont("Times-Bold", 18)
    c.drawCentredString(width / 2, height - 380, course)

    c.setFont("Times-Roman", 14)
    c.drawCentredString(width / 2, height - 420, "with outstanding performance.")

    # Footer Lines
    c.line(120, 150, 260, 150)
    c.line(width - 260, 150, width - 120, 150)

    c.setFont("Times-Roman", 12)
    c.drawCentredString(190, 130, "Instructor")
    c.drawCentredString(width - 190, 130, "Date")

    # Date Value
    today = datetime.now().strftime("%d %B %Y")
    c.drawCentredString(width - 190, 110, today)

    # Institution
    c.setFont("Times-Italic", 12)
    c.drawCentredString(width / 2, 90, institution)

    # Hash (small, bottom)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 70, f"Certificate Hash: {hash_val}")

    c.save()

    # ---------------- QR CODE ---------------- #
    verify_url = f"http://{SERVER_IP}:{SERVER_PORT}/verify?hash={hash_val}"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)

    return pdf_path, qr_path
