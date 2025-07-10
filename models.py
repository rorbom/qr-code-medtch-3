from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class MedicalProfile(db.Model):
    __tablename__ = 'medical_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    blood_type = db.Column(db.String(5), nullable=True)
    allergy = db.Column(db.Text, nullable=True)
    condition = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(200), nullable=True)
    last_checkup_date = db.Column(db.Date, nullable=True)
    last_checkup_details = db.Column(db.Text, nullable=True)
    doctor_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicalProfile {self.username}: {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'blood_type': self.blood_type,
            'allergy': self.allergy,
            'condition': self.condition,
            'emergency_contact': self.emergency_contact,
            'last_checkup_date': self.last_checkup_date.isoformat() if self.last_checkup_date else None,
            'last_checkup_details': self.last_checkup_details,
            'doctor_notes': self.doctor_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
