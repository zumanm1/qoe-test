from datetime import datetime, timedelta
from app import db

class NetworkElement(db.Model):
    __tablename__ = 'network_elements'
    
    id = db.Column(db.Integer, primary_key=True)
    element_name = db.Column(db.String(100), nullable=False, unique=True)
    element_type = db.Column(db.String(50), nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    subdomain = db.Column(db.String(50), nullable=True)
    protocol_layer = db.Column(db.String(50))
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    kpi_measurements = db.relationship('KPIMeasurement', backref='element', lazy='dynamic')
    
    def get_latest_kpis(self):
        """Get the latest KPI measurements for this element"""
        from sqlalchemy import func
        from app.models.network import KPIDefinition
        
        subquery = db.session.query(
            KPIMeasurement.kpi_id,
            func.max(KPIMeasurement.timestamp).label('max_time')
        ).filter_by(element_id=self.id).group_by(KPIMeasurement.kpi_id).subquery('t')
        
        latest_kpis = db.session.query(KPIMeasurement).join(
            subquery,
            db.and_(
                KPIMeasurement.kpi_id == subquery.c.kpi_id,
                KPIMeasurement.timestamp == subquery.c.max_time
            )
        ).join(KPIDefinition).filter(KPIMeasurement.element_id == self.id).all()
        
        return {
            kpi.definition.kpi_code: {
                'value': kpi.value,
                'timestamp': kpi.timestamp,
                'quality_score': kpi.quality_score
            } for kpi in latest_kpis
        }
    
    def get_kpi_history(self, kpi_code, hours=24):
        """Get historical KPI measurements for this element"""
        from app.models.network import KPIDefinition
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.kpi_measurements.join(KPIDefinition).filter(
            KPIDefinition.kpi_code == kpi_code,
            KPIMeasurement.timestamp > cutoff
        ).order_by(KPIMeasurement.timestamp).all()
    
    def __repr__(self):
        return f'<NetworkElement {self.element_name} ({self.domain})>'


class KPIDefinition(db.Model):
    __tablename__ = 'kpi_definitions'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_name = db.Column(db.String(100), nullable=False)
    kpi_code = db.Column(db.String(50), unique=True, nullable=False)
    unit = db.Column(db.String(20))
    domain = db.Column(db.String(50))
    impact_level = db.Column(db.String(20))
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    optimal_value = db.Column(db.Float)
    description = db.Column(db.Text)
    
    # Relationships
    measurements = db.relationship('KPIMeasurement', backref='definition', lazy='dynamic')
    
    def is_critical(self, value):
        """Determine if a KPI value is in critical range"""
        if self.impact_level != 'high':
            return False
        
        # Check if value is outside acceptable range
        if self.optimal_value:
            deviation = abs(value - self.optimal_value) / self.optimal_value
            return deviation > 0.3  # 30% deviation is critical
        
        return False
    
    def __repr__(self):
        return f'<KPIDefinition {self.kpi_code}>'


class KPIMeasurement(db.Model):
    __tablename__ = 'kpi_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    element_id = db.Column(db.Integer, db.ForeignKey('network_elements.id'), nullable=False)
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpi_definitions.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    quality_score = db.Column(db.Float)
    
    __table_args__ = (
        db.Index('idx_element_kpi', 'element_id', 'kpi_id'),
    )
    
    def to_dict(self):
        return {
            'element': self.element.element_name,
            'kpi': self.definition.kpi_code,
            'value': self.value,
            'unit': self.definition.unit,
            'timestamp': self.timestamp.isoformat(),
            'quality_score': self.quality_score
        }
    
    def __repr__(self):
        return f'<KPIMeasurement {self.definition.kpi_code}={self.value}{self.definition.unit or ""}>'


class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    element_id = db.Column(db.Integer, db.ForeignKey('network_elements.id'))
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpi_definitions.id'))
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    
    # Relationships
    element = db.relationship('NetworkElement')
    definition = db.relationship('KPIDefinition')
    
    def to_dict(self):
        return {
            'id': self.id,
            'element': self.element.element_name if self.element else None,
            'kpi': self.definition.kpi_code if self.definition else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'acknowledged': self.acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }
    
    def __repr__(self):
        return f'<Alert {self.severity}: {self.alert_type}>'
