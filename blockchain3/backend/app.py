import os
from flask import Flask, render_template, request, send_from_directory
from flask_login import LoginManager, login_required, current_user
import pandas as pd

from database import db, Certificate, User
from certificate import generate_hash, generate_certificate
from blockchain import store_on_blockchain
from auth import auth

# ---------------- PATH CONFIG ---------------- #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
CERT_PDF_DIR = os.path.join(BASE_DIR, "certificates", "pdf")

# ---------------- FLASK APP ---------------- #

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

app.secret_key = "secret123"

# ---------------- DATABASE ---------------- #

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "certificates.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ---------------- LOGIN ---------------- #

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- BLUEPRINT ---------------- #

app.register_blueprint(auth)

# ---------------- CREATE TABLES ---------------- #

with app.app_context():
    db.create_all()

# ---------------- ROUTES ---------------- #

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/institute")
@login_required
def institute_dashboard():
    if current_user.role != "institute":
        return "Unauthorized Access"
    return render_template("institute_dashboard.html")

@app.route("/student")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return "Unauthorized Access"

    certs = Certificate.query.filter_by(email=current_user.email).all()
    return render_template("student_dashboard.html", certs=certs)

# ---------------- EXCEL UPLOAD ---------------- #

@app.route("/upload", methods=["POST"])
@login_required
def upload_excel():
    if current_user.role != "institute":
        return "Unauthorized Access"

    file = request.files["file"]
    df = pd.read_excel(file)

    created = 0
    skipped = 0

    for _, row in df.iterrows():
        data = f"{row['Student_ID']}{row['Student_Name']}{row['Course']}{row['Issue_Date']}"
        hash_val = generate_hash(data)

        if Certificate.query.filter_by(hash_value=hash_val).first():
            skipped += 1
            continue

        pdf_path, qr_path = generate_certificate(
            row["Student_Name"],
            row["Course"],
            row["Institution"],
            hash_val
        )

        cert = Certificate(
            student_id=row["Student_ID"],
            student_name=row["Student_Name"],
            email=row["Email"],
            course=row["Course"],
            institution=row["Institution"],
            issue_date=str(row["Issue_Date"]),
            hash_value=hash_val,
            pdf_path=pdf_path,
            qr_path=qr_path
        )

        db.session.add(cert)
        store_on_blockchain(hash_val)
        created += 1

    db.session.commit()

    return render_template(
        "upload_result.html",
        created=created,
        skipped=skipped
    )

# ---------------- VERIFY ---------------- #

@app.route("/verify", methods=["GET", "POST"])
def verify():
    cert = None

    hash_val = request.args.get("hash")
    if hash_val:
        cert = Certificate.query.filter_by(hash_value=hash_val).first()
        return render_template("verify.html", cert=cert)

    if request.method == "POST":
        hash_val = request.form["hash"]
        cert = Certificate.query.filter_by(hash_value=hash_val).first()

    return render_template("verify.html", cert=cert)

# ---------------- DOWNLOAD CERTIFICATE (FIX) ---------------- #

@app.route("/download/<filename>")
@login_required
def download_certificate(filename):
    return send_from_directory(
        CERT_PDF_DIR,
        filename,
        as_attachment=True
    )

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
