from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  # institute / student
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50))
    student_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    course = db.Column(db.String(100))
    institution = db.Column(db.String(100))
    issue_date = db.Column(db.String(50))
    hash_value = db.Column(db.String(256), unique=True)
    pdf_path = db.Column(db.String(200))
    qr_path = db.Column(db.String(200))
