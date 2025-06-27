import math
import numpy as np
from app.models.simulation import OptimizationRecommendation
from app import db

class SimulationEngine:
    def __init__(self):
        # Define domain weights for QoE calculation
        self.domain_weights = {
            'ran': 0.4,        # Radio Access Network has highest impact on QoE
            'transport': 0.3,  # Transport network has significant impact
            'core': 0.2,       # Core network has moderate impact
            'internet': 0.1    # Internet connectivity has lowest direct impact
        }
        
        # Define parameter ranges for validation
        self.param_ranges = {
            'sinr': (-5, 30),             # dB
            'prb_utilization': (0, 100),  # %
            'connected_users': (10, 500), # users
            'bler': (0, 30),              # %
            'mpls_utilization': (0, 100), # %
            'lsp_flapping': (0, 10),      # events/hr
            'gtp_efficiency': (70, 100),  # %
            'bearer_rate': (10, 500)      # Mbps
        }
        
        # Define default parameters
        self.default_params = {
            'sinr': 15,               # dB
            'prb_utilization': 50,    # %
            'connected_users': 100,   # users
            'bler': 5,                # %
            'mpls_utilization': 60,   # %
            'lsp_flapping': 0,        # events/hr
            'gtp_efficiency': 90,     # %
            'bearer_rate': 100        # Mbps
        }
    
    def calculate_qoe(self, params=None):
        """
        Calculate QoE score based on network parameters across all domains
        Returns a dict with QoE score, performance metrics and domain impacts
        """
        # Use provided parameters or defaults
        params = params or self.default_params
        
        # Validate and normalize parameters
        validated_params = self._validate_params(params)
        
        # Calculate domain-specific impacts
        domain_impacts = {
            'ran': self._calculate_ran_impact(validated_params),
            'transport': self._calculate_transport_impact(validated_params),
            'core': self._calculate_core_impact(validated_params),
            'internet': self._calculate_internet_impact(validated_params)
        }
        
        # Calculate overall QoE score (0-100)
        qoe_score = sum(impact * self.domain_weights[domain] for domain, impact in domain_impacts.items())
        
        # Calculate performance metrics
        download_speed = self._calculate_download_speed(validated_params)
        upload_speed = self._calculate_upload_speed(validated_params)
        latency = self._calculate_latency(validated_params)
        jitter = self._calculate_jitter(validated_params)
        packet_loss = self._calculate_packet_loss(validated_params)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validated_params, domain_impacts)
        
        return {
            'qoe_score': qoe_score,
            'quality_rating': self._get_quality_rating(qoe_score),
            'performance_metrics': {
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'latency': latency,
                'jitter': jitter,
                'packet_loss': packet_loss
            },
            'domain_impacts': domain_impacts,
            'recommendations': recommendations
        }
    
    def _validate_params(self, params):
        """Validate and clamp parameters to valid ranges"""
        validated = {}
        
        # Use default values for missing parameters
        for param, (min_val, max_val) in self.param_ranges.items():
            value = params.get(param, self.default_params.get(param, 0))
            # Clamp value to valid range
            validated[param] = max(min_val, min(value, max_val))
        
        return validated
    
    def _get_quality_rating(self, score):
        """Convert numeric QoE score to qualitative rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Very Poor"
    
    def _calculate_ran_impact(self, params):
        """Calculate RAN domain impact (0-100)"""
        # SINR has logarithmic impact on quality
        sinr_impact = 50 + 50 * (math.tanh((params['sinr'] - 10) / 10))
        
        # PRB utilization - high utilization reduces quality
        prb_impact = 100 - params['prb_utilization'] * 0.5
        
        # Connected users - impact is based on a logistic function
        users = params['connected_users']
        user_impact = 100 / (1 + math.exp((users - 250) / 50))
        
        # BLER (Block Error Rate) - directly reduces quality
        bler_impact = 100 - params['bler'] * 3
        
        # Weighted combination of all factors
        return 0.4 * sinr_impact + 0.3 * prb_impact + 0.2 * user_impact + 0.1 * bler_impact
    
    def _calculate_transport_impact(self, params):
        """Calculate Transport domain impact (0-100)"""
        # MPLS tunnel utilization - high utilization reduces quality
        mpls_impact = 100 - params['mpls_utilization'] * 0.8
        
        # LSP flapping - each flap significantly reduces quality
        flap_impact = 100 - params['lsp_flapping'] * 10
        
        return 0.7 * mpls_impact + 0.3 * flap_impact
    
    def _calculate_core_impact(self, params):
        """Calculate Core domain impact (0-100)"""
        # GTP-U tunnel efficiency - directly impacts quality
        gtp_impact = params['gtp_efficiency']
        
        # Bearer rate - impact is based on logarithmic function
        rate = params['bearer_rate']
        rate_impact = min(100, 20 * math.log10(rate))
        
        return 0.6 * gtp_impact + 0.4 * rate_impact
    
    def _calculate_internet_impact(self, params):
        """Calculate Internet domain impact (0-100)"""
        # For now, using a fixed value as internet conditions are external
        # In a real system, this would incorporate internet peering metrics
        return 85
    
    def _calculate_download_speed(self, params):
        """Calculate expected download speed in Mbps"""
        # Base speed determined by bearer rate
        base_speed = params['bearer_rate']
        
        # Adjust based on RAN conditions
        sinr_factor = 1 - (30 - params['sinr']) / 40
        prb_factor = 1 - params['prb_utilization'] / 200
        user_factor = 1 - math.log10(params['connected_users']) / 5
        
        # Adjust based on core efficiency
        gtp_factor = params['gtp_efficiency'] / 100
        
        speed = base_speed * sinr_factor * prb_factor * user_factor * gtp_factor
        
        # Ensure reasonable bounds
        return max(0.1, min(speed, params['bearer_rate']))
    
    def _calculate_upload_speed(self, params):
        """Calculate expected upload speed in Mbps"""
        # Upload is typically lower than download
        return self._calculate_download_speed(params) * 0.2
    
    def _calculate_latency(self, params):
        """Calculate expected end-to-end latency in ms"""
        # Air interface latency
        sinr = params['sinr']
        air_latency = 5 + max(0, (15 - sinr) * 2)
        
        # Transport network latency
        transport_latency = 10 + (params['mpls_utilization'] / 10) + (params['lsp_flapping'] * 5)
        
        # Core network latency
        core_latency = 5 + (100 - params['gtp_efficiency']) / 3
        
        # Internet latency (fixed for now)
        internet_latency = 20
        
        return air_latency + transport_latency + core_latency + internet_latency
    
    def _calculate_jitter(self, params):
        """Calculate expected jitter in ms"""
        # Base jitter is affected by multiple factors
        base_jitter = 2
        
        # RAN variability
        if params['sinr'] < 10:
            base_jitter += (10 - params['sinr']) * 0.3
        
        # Transport variability
        if params['mpls_utilization'] > 70:
            base_jitter += (params['mpls_utilization'] - 70) * 0.2
        
        if params['lsp_flapping'] > 0:
            base_jitter += params['lsp_flapping'] * 1.5
        
        return base_jitter
    
    def _calculate_packet_loss(self, params):
        """Calculate expected packet loss percentage"""
        # Base loss from RAN
        ran_loss = params['bler'] * 0.1
        
        # Loss from transport network
        transport_loss = 0
        if params['mpls_utilization'] > 80:
            transport_loss = (params['mpls_utilization'] - 80) * 0.1
        
        # Loss from core network
        core_loss = (100 - params['gtp_efficiency']) * 0.01
        
        return ran_loss + transport_loss + core_loss
    
    def _generate_recommendations(self, params, impacts):
        """Generate optimization recommendations based on parameters and domain impacts"""
        recommendations = []
        
        # RAN recommendations
        if params['sinr'] < 10:
            recommendations.append({
                'domain': 'ran',
                'severity': 'high',
                'recommendation': 'Improve signal quality (SINR) by optimizing antenna tilt or transmit power.',
                'impact_estimate': 0.2
            })
        
        if params['prb_utilization'] > 80:
            recommendations.append({
                'domain': 'ran',
                'severity': 'medium',
                'recommendation': 'High PRB utilization detected. Consider adding carrier aggregation or new cells to offload traffic.',
                'impact_estimate': 0.15
            })
        
        if params['bler'] > 10:
            recommendations.append({
                'domain': 'ran',
                'severity': 'high',
                'recommendation': 'High block error rate detected. Check for interference sources or adjust modulation and coding scheme.',
                'impact_estimate': 0.18
            })
        
        # Transport recommendations
        if params['mpls_utilization'] > 85:
            recommendations.append({
                'domain': 'transport',
                'severity': 'high',
                'recommendation': 'MPLS tunnel utilization is critical. Increase bandwidth or implement traffic engineering.',
                'impact_estimate': 0.25
            })
        
        if params['lsp_flapping'] > 2:
            recommendations.append({
                'domain': 'transport',
                'severity': 'high',
                'recommendation': 'Excessive LSP flapping detected. Check for network instability or equipment issues.',
                'impact_estimate': 0.3
            })
        
        # Core recommendations
        if params['gtp_efficiency'] < 85:
            recommendations.append({
                'domain': 'core',
                'severity': 'medium',
                'recommendation': 'Low GTP tunnel efficiency. Optimize packet handling or check for fragmentation issues.',
                'impact_estimate': 0.12
            })
        
        if params['bearer_rate'] < 50:
            recommendations.append({
                'domain': 'core',
                'severity': 'low',
                'recommendation': 'Consider increasing bearer QoS rate to improve potential throughput.',
                'impact_estimate': 0.08
            })
        
        return recommendations
    
    def save_recommendations_to_db(self, scenario_id, recommendations):
        """Save generated recommendations to database"""
        for rec in recommendations:
            db_rec = OptimizationRecommendation(
                scenario_id=scenario_id,
                domain=rec['domain'],
                severity=rec['severity'],
                recommendation=rec['recommendation'],
                impact_estimate=rec['impact_estimate']
            )
            db.session.add(db_rec)
        
        db.session.commit()
