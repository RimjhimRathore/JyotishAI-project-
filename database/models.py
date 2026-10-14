from .db import db
from flask_login import UserMixin
from datetime import datetime

class KundaliRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    dob = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    place = db.Column(db.String(200), nullable=False)
    chart_json = db.Column(db.Text, nullable=False)     # calculated chart
    reading_json = db.Column(db.Text, nullable=False)   # AI reading
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserDetails(UserMixin, db.Model):
    __tablename__ = "user_details"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class BirthChart(db.Model):
    __tablename__ = "birthchart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_details.id"))

    name = db.Column(db.String(100))
    birth_date = db.Column(db.String(50))
    birth_time = db.Column(db.String(50))
    birth_place = db.Column(db.String(100))
