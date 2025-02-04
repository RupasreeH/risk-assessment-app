import uuid
from flask_login import UserMixin
from riskassessmentapp.app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    uid = db.Column(db.String(36), unique=True, nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User: {self.username}>'
    
    def get_id(self):
        return self.uid
    
    def to_json_response(self):
        return {
            "uid": self.uid,
            "email":self.email,
            "firstName":self.first_name,
            "lastName":self.last_name
        }
        
