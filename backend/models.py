from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile management."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    company = db.Column(db.String(100))
    role = db.Column(db.String(50), default='user')  # user, admin, enterprise
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # Only keep wordclouds relationship
    wordclouds = db.relationship('WordCloud', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class WordCloud(db.Model):
    """WordCloud model for storing generated word clouds."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Text and processing data
    original_text = db.Column(db.Text)
    processed_text = db.Column(db.Text)
    text_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    unique_words = db.Column(db.Integer)
    
    # Word cloud settings
    settings = db.Column(db.Text)  # JSON string of settings
    mask_shape = db.Column(db.String(50))
    color_scheme = db.Column(db.String(50))
    background_color = db.Column(db.String(20))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    
    # Generated data
    word_frequencies = db.Column(db.Text)  # JSON string
    sentiment_analysis = db.Column(db.Text)  # JSON string
    topic_analysis = db.Column(db.Text)  # JSON string
    readability_metrics = db.Column(db.Text)  # JSON string
    
    # File storage
    image_path = db.Column(db.String(255))
    image_base64 = db.Column(db.Text)  # For immediate display
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text)  # JSON string of tags
    
    def get_settings(self):
        """Get settings as dictionary."""
        return json.loads(self.settings) if self.settings else {}
    
    def set_settings(self, settings_dict):
        """Set settings from dictionary."""
        self.settings = json.dumps(settings_dict)
    
    def get_word_frequencies(self):
        """Get word frequencies as dictionary."""
        return json.loads(self.word_frequencies) if self.word_frequencies else {}
    
    def set_word_frequencies(self, frequencies_dict):
        """Set word frequencies from dictionary."""
        self.word_frequencies = json.dumps(frequencies_dict)
    
    def get_sentiment_analysis(self):
        """Get sentiment analysis as dictionary."""
        return json.loads(self.sentiment_analysis) if self.sentiment_analysis else {}
    
    def set_sentiment_analysis(self, sentiment_dict):
        """Set sentiment analysis from dictionary."""
        self.sentiment_analysis = json.dumps(sentiment_dict)
    
    def get_tags(self):
        """Get tags as list."""
        return json.loads(self.tags) if self.tags else []
    
    def set_tags(self, tags_list):
        """Set tags from list."""
        self.tags = json.dumps(tags_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'text_length': self.text_length,
            'word_count': self.word_count,
            'unique_words': self.unique_words,
            'mask_shape': self.mask_shape,
            'color_scheme': self.color_scheme,
            'background_color': self.background_color,
            'width': self.width,
            'height': self.height,
            'settings': self.get_settings(),
            'word_frequencies': self.get_word_frequencies(),
            'sentiment_analysis': self.get_sentiment_analysis(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_public': self.is_public,
            'tags': self.get_tags(),
            'image_base64': self.image_base64
        }

class Analytics(db.Model):
    """Analytics model for tracking user actions and system usage."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50))  # e.g., 'generate_wordcloud', 'login', 'export'
    feature_used = db.Column(db.String(50))  # e.g., 'wordcloud', 'templates', 'export'
    resource_id = db.Column(db.Integer)  # ID of the resource being acted upon if applicable
    text_length = db.Column(db.Integer)  # Length of text processed if applicable
    processing_time = db.Column(db.Float)  # Time taken to process in seconds
    referrer = db.Column(db.String(255))  # Where the action was initiated from
    user_agent = db.Column(db.String(255))  # User agent information
    ip_address = db.Column(db.String(45))  # IP address
    is_error = db.Column(db.Boolean, default=False)  # Whether an error occurred
    error_message = db.Column(db.Text)  # Error message if applicable
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action': self.action,
            'feature_used': self.feature_used,
            'resource_id': self.resource_id,
            'text_length': self.text_length,
            'processing_time': self.processing_time,
            'is_error': self.is_error
        } 