from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_type = db.Column(db.String(50), nullable=True)  # Store file type, if applicable
    file_size = db.Column(db.Integer, nullable=True)  # Store file size, if applicable
    unique_id = db.Column(db.String(100), nullable=True)  # Store a unique identifier for the document
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('documents', lazy=True))
    
    def __repr__(self):
        return f'<Document {self.title}>'

class OcrResult(db.Model):
    __tablename__ = 'ocr_results'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    confidence_scores = db.Column(db.JSON, nullable=True)  # Store confidence scores for the OCR results
    bounding_boxes = db.Column(db.JSON, nullable=True)  # Store bounding boxes for the detected text
    language = db.Column(db.String(50), nullable=True)  # Store the language of the detected text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    document = db.relationship('Document', backref=db.backref('ocr_results', lazy=True))
    
    def __repr__(self):
        return f'<OcrResult {self.id}>'
