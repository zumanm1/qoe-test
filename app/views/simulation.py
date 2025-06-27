from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.simulation import SimulationScenario, PerformanceTest, OptimizationRecommendation
from app.services.simulation import SimulationEngine
import json
from datetime import datetime

# Create simulation blueprint
simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/')
@login_required
def index():
    """Main simulation view with parameter controls"""
    # Initialize simulation engine to get parameter ranges
    engine = SimulationEngine()
    param_ranges = engine.param_ranges
    default_params = engine.default_params
    
    # Get saved scenarios for the current user
    scenarios = SimulationScenario.query.filter_by(
        created_by_id=current_user.id
    ).order_by(SimulationScenario.created_at.desc()).all()
    
    return render_template(
        'simulation/index.html',
        title='QoE Simulation Engine',
        param_ranges=param_ranges,
        default_params=default_params,
        scenarios=scenarios
    )


@simulation_bp.route('/api/calculate', methods=['POST'])
@login_required
def calculate_qoe():
    """API endpoint to calculate QoE based on provided parameters"""
    # Get parameters from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No parameters provided'}), 400
    
    # Initialize simulation engine
    engine = SimulationEngine()
    
    # Calculate QoE with provided parameters
    result = engine.calculate_qoe(data)
    
    return jsonify(result)


@simulation_bp.route('/api/scenarios', methods=['GET'])
@login_required
def get_scenarios():
    """API endpoint to get saved scenarios"""
    scenarios = SimulationScenario.query.filter_by(
        created_by_id=current_user.id
    ).order_by(SimulationScenario.created_at.desc()).all()
    
    result = [{
        'id': s.id,
        'name': s.scenario_name,
        'description': s.description,
        'created_at': s.created_at.isoformat(),
        'is_baseline': s.is_baseline
    } for s in scenarios]
    
    return jsonify(result)


@simulation_bp.route('/api/scenarios', methods=['POST'])
@login_required
def save_scenario():
    """API endpoint to save a simulation scenario"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract details
    name = data.get('name')
    description = data.get('description', '')
    parameters = data.get('parameters', {})
    test_results = data.get('test_results', {})
    
    if not name or not parameters:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create scenario
    scenario = SimulationScenario(
        scenario_name=name,
        description=description,
        created_by_id=current_user.id,
        created_at=datetime.utcnow()
    )
    scenario.set_parameters(parameters)
    
    # Add to database
    db.session.add(scenario)
    db.session.commit()
    
    # Create performance test record for this scenario
    if test_results:
        test = PerformanceTest(
            scenario_id=scenario.id,
            test_type='simulation',
            download_speed=test_results.get('download_speed'),
            upload_speed=test_results.get('upload_speed'),
            latency=test_results.get('latency'),
            jitter=test_results.get('jitter', 0),
            packet_loss=test_results.get('packet_loss', 0),
            qoe_score=test_results.get('qoe_score'),
            timestamp=datetime.utcnow()
        )
        db.session.add(test)
    
    # Save recommendations
    recommendations = test_results.get('recommendations', [])
    engine = SimulationEngine()
    engine.save_recommendations_to_db(scenario.id, recommendations)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'scenario_id': scenario.id,
        'message': f'Scenario "{name}" saved successfully'
    })


@simulation_bp.route('/api/scenarios/<int:scenario_id>', methods=['GET'])
@login_required
def get_scenario(scenario_id):
    """API endpoint to get a specific scenario"""
    scenario = SimulationScenario.query.get(scenario_id)
    
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    
    # Check if the user has access to this scenario
    if scenario.created_by_id != current_user.id and not current_user.has_role('admin'):
        return jsonify({'error': 'You do not have permission to view this scenario'}), 403
    
    # Get test results for this scenario
    test = PerformanceTest.query.filter_by(scenario_id=scenario.id).first()
    
    # Get recommendations for this scenario
    recommendations = OptimizationRecommendation.query.filter_by(scenario_id=scenario.id).all()
    
    result = {
        'id': scenario.id,
        'name': scenario.scenario_name,
        'description': scenario.description,
        'created_at': scenario.created_at.isoformat(),
        'is_baseline': scenario.is_baseline,
        'parameters': scenario.get_parameters(),
        'test_results': test.to_dict() if test else None,
        'recommendations': [r.to_dict() for r in recommendations]
    }
    
    return jsonify(result)


@simulation_bp.route('/scenarios/<int:scenario_id>')
@login_required
def view_scenario(scenario_id):
    """View details for a specific scenario"""
    scenario = SimulationScenario.query.get_or_404(scenario_id)
    
    # Check if the user has access to this scenario
    if scenario.created_by_id != current_user.id and not current_user.has_role('admin'):
        flash('You do not have permission to view this scenario', 'danger')
        return redirect(url_for('simulation.index'))
    
    # Get test results
    test = PerformanceTest.query.filter_by(scenario_id=scenario.id).first()
    
    # Get recommendations
    recommendations = OptimizationRecommendation.query.filter_by(scenario_id=scenario.id).all()
    
    # Initialize simulation engine to get parameter ranges
    engine = SimulationEngine()
    param_ranges = engine.param_ranges
    
    return render_template(
        'simulation/scenario.html',
        title=f'Scenario: {scenario.scenario_name}',
        scenario=scenario,
        parameters=scenario.get_parameters(),
        test=test,
        recommendations=recommendations,
        param_ranges=param_ranges
    )


@simulation_bp.route('/compare')
@login_required
def compare():
    """Compare two scenarios side by side"""
    # Get scenario IDs from request parameters
    scenario1_id = request.args.get('scenario1', type=int)
    scenario2_id = request.args.get('scenario2', type=int)
    
    # Get all scenarios for selection
    scenarios = SimulationScenario.query.filter_by(
        created_by_id=current_user.id
    ).order_by(SimulationScenario.created_at.desc()).all()
    
    scenario1 = None
    scenario2 = None
    comparison = None
    
    # If both scenarios are selected, get their details
    if scenario1_id and scenario2_id:
        scenario1 = SimulationScenario.query.get(scenario1_id)
        scenario2 = SimulationScenario.query.get(scenario2_id)
        
        if scenario1 and scenario2:
            # Get test results
            test1 = PerformanceTest.query.filter_by(scenario_id=scenario1.id).first()
            test2 = PerformanceTest.query.filter_by(scenario_id=scenario2.id).first()
            
            # Compare parameters
            comparison = {
                'parameters': scenario1.compare_with(scenario2),
                'test1': test1.to_dict() if test1 else None,
                'test2': test2.to_dict() if test2 else None
            }
    
    return render_template(
        'simulation/compare.html',
        title='Compare Scenarios',
        scenarios=scenarios,
        scenario1=scenario1,
        scenario2=scenario2,
        comparison=comparison
    )
