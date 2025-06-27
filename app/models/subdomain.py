"""
Subdomain model for Mobile QoE Tool
This defines the relationship between main domains and their subdomains
"""
from datetime import datetime
from app import db

class NetworkSubdomain(db.Model):
    """Model for network subdomains within main domains"""
    __tablename__ = 'network_subdomains'
    
    id = db.Column(db.Integer, primary_key=True)
    subdomain_name = db.Column(db.String(100), nullable=False, unique=True)
    parent_domain = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NetworkSubdomain {self.subdomain_name}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'subdomain_name': self.subdomain_name,
            'parent_domain': self.parent_domain,
            'description': self.description
        }
