from datetime import datetime
from app import db
import json

class SimulationScenario(db.Model):
    __tablename__ = 'simulation_scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_baseline = db.Column(db.Boolean, default=False)
    parameters = db.Column(db.Text)  # JSON string
    
    # Relationships
    performance_tests = db.relationship('PerformanceTest', backref='scenario', lazy='dynamic')
    recommendations = db.relationship('OptimizationRecommendation', backref='scenario', lazy='dynamic')
    
    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}
    
    def set_parameters(self, params):
        self.parameters = json.dumps(params)
    
    def calculate_qoe(self):
        from app.services.simulation import SimulationEngine
        engine = SimulationEngine()
        return engine.calculate_qoe(self.get_parameters())
    
    def compare_with(self, other_scenario):
        """Compare this scenario with another scenario"""
        params1 = self.get_parameters()
        params2 = other_scenario.get_parameters()
        
        differences = {}
        all_keys = set(params1.keys()) | set(params2.keys())
        
        for key in all_keys:
            val1 = params1.get(key, 0)
            val2 = params2.get(key, 0)
            if val1 != val2:
                differences[key] = {
                    'scenario1': val1,
                    'scenario2': val2,
                    'difference': val2 - val1,
                    'percentage': ((val2 - val1) / val1 * 100) if val1 != 0 else 0
                }
        
        return differences
    
    def __repr__(self):
        return f'<SimulationScenario {self.scenario_name}>'


class PerformanceTest(db.Model):
    __tablename__ = 'performance_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50))
    scenario_id = db.Column(db.Integer, db.ForeignKey('simulation_scenarios.id'))
    download_speed = db.Column(db.Float)
    upload_speed = db.Column(db.Float)
    latency = db.Column(db.Float)
    jitter = db.Column(db.Float)
    packet_loss = db.Column(db.Float)
    qoe_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    test_duration = db.Column(db.Integer)
    server_location = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'test_type': self.test_type,
            'download_speed': self.download_speed,
            'upload_speed': self.upload_speed,
            'latency': self.latency,
            'jitter': self.jitter,
            'packet_loss': self.packet_loss,
            'qoe_score': self.qoe_score,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<PerformanceTest {self.test_type} QoE:{self.qoe_score}>'


class OptimizationRecommendation(db.Model):
    __tablename__ = 'optimization_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('simulation_scenarios.id'))
    domain = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    recommendation = db.Column(db.Text, nullable=False)
    impact_estimate = db.Column(db.Float)  # Estimated QoE improvement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    implemented = db.Column(db.Boolean, default=False)
    implemented_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    implemented_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'severity': self.severity,
            'recommendation': self.recommendation,
            'impact_estimate': self.impact_estimate,
            'created_at': self.created_at.isoformat(),
            'implemented': self.implemented
        }
    
    def __repr__(self):
        return f'<OptimizationRecommendation {self.id}: {self.domain}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    
    def __repr__(self):
        return f'<AuditLog {self.action} by user {self.user_id}>'
