from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from app.models.network import NetworkElement, KPIMeasurement, KPIDefinition
from app.models.simulation import SimulationScenario, PerformanceTest
from datetime import datetime, timedelta
import json
import io
import csv
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Create reports blueprint
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Main reports dashboard"""
    # Get available time ranges
    time_ranges = [
        ('day', 'Last 24 Hours'),
        ('week', 'Last 7 Days'),
        ('month', 'Last 30 Days')
    ]
    
    # Get domains for filtering
    domains = ['ran', 'transport', 'core', 'internet', 'e2e']
    
    # Get report types
    report_types = [
        ('kpi_trends', 'KPI Trends'),
        ('domain_health', 'Domain Health'),
        ('qoe_analysis', 'QoE Analysis'),
        ('alerts_summary', 'Alerts Summary')
    ]
    
    return render_template(
        'reports/index.html',
        title='Network Reports',
        time_ranges=time_ranges,
        domains=domains,
        report_types=report_types
    )


@reports_bp.route('/kpi/trends')
@login_required
def kpi_trends():
    """KPI trend analysis report"""
    # Get parameters
    domain = request.args.get('domain', 'ran')
    time_range = request.args.get('time_range', 'day')
    kpi_code = request.args.get('kpi_code')
    
    # Set time range
    if time_range == 'day':
        cutoff = datetime.utcnow() - timedelta(hours=24)
        interval = 'hourly'
    elif time_range == 'week':
        cutoff = datetime.utcnow() - timedelta(days=7)
        interval = 'daily'
    elif time_range == 'month':
        cutoff = datetime.utcnow() - timedelta(days=30)
        interval = 'weekly'
    else:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        interval = 'hourly'
    
    # Get KPI definitions for the domain
    kpi_defs = KPIDefinition.query.filter_by(domain=domain).all()
    
    # If no specific KPI is selected, use the first one
    if not kpi_code and kpi_defs:
        kpi_code = kpi_defs[0].kpi_code
    
    selected_kpi = None
    for kpi in kpi_defs:
        if kpi.kpi_code == kpi_code:
            selected_kpi = kpi
            break
    
    # Get measurements for selected KPI
    measurements = []
    if selected_kpi:
        measurements = KPIMeasurement.query.join(KPIDefinition).filter(
            KPIDefinition.kpi_code == kpi_code,
            KPIMeasurement.timestamp >= cutoff
        ).order_by(KPIMeasurement.timestamp).all()
    
    return render_template(
        'reports/kpi_trends.html',
        title=f'KPI Trends - {domain.upper()}',
        domain=domain,
        time_range=time_range,
        kpi_defs=kpi_defs,
        selected_kpi=selected_kpi,
        measurements=measurements,
        interval=interval
    )


@reports_bp.route('/domain/health')
@login_required
def domain_health():
    """Domain health report"""
    # Get parameters
    time_range = request.args.get('time_range', 'day')
    
    # Set time range
    if time_range == 'day':
        cutoff = datetime.utcnow() - timedelta(hours=24)
    elif time_range == 'week':
        cutoff = datetime.utcnow() - timedelta(days=7)
    elif time_range == 'month':
        cutoff = datetime.utcnow() - timedelta(days=30)
    else:
        cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # Get health status by domain
    domains = ['ran', 'transport', 'core', 'internet']
    domain_health = {}
    
    for domain in domains:
        # Get all elements in this domain
        elements = NetworkElement.query.filter_by(domain=domain).all()
        
        # Count active vs inactive
        total = len(elements)
        active = sum(1 for e in elements if e.status == 'active')
        
        # Calculate health percentage
        health = int((active / total * 100) if total > 0 else 0)
        
        # Get average quality scores for critical KPIs
        kpi_scores = []
        kpi_defs = KPIDefinition.query.filter_by(domain=domain, is_critical=True).all()
        
        for element in elements:
            for kpi_def in kpi_defs:
                # Get latest measurement
                measurement = KPIMeasurement.query.join(KPIDefinition).filter(
                    KPIMeasurement.element_id == element.id,
                    KPIDefinition.id == kpi_def.id,
                    KPIMeasurement.timestamp >= cutoff
                ).order_by(KPIMeasurement.timestamp.desc()).first()
                
                if measurement and measurement.quality_score is not None:
                    kpi_scores.append(measurement.quality_score)
        
        # Calculate average quality score
        avg_quality = sum(kpi_scores) / len(kpi_scores) if kpi_scores else 0
        
        domain_health[domain] = {
            'health': health,
            'active': active,
            'total': total,
            'avg_quality': avg_quality,
            'kpi_count': len(kpi_scores)
        }
    
    return render_template(
        'reports/domain_health.html',
        title='Domain Health Report',
        time_range=time_range,
        domain_health=domain_health
    )


@reports_bp.route('/qoe/analysis')
@login_required
def qoe_analysis():
    """QoE analysis report"""
    # Get performance tests from the last 30 days
    cutoff = datetime.utcnow() - timedelta(days=30)
    tests = PerformanceTest.query.filter(
        PerformanceTest.timestamp >= cutoff
    ).order_by(PerformanceTest.timestamp.desc()).all()
    
    # Organize tests by date
    tests_by_date = {}
    for test in tests:
        date_key = test.timestamp.strftime('%Y-%m-%d')
        if date_key not in tests_by_date:
            tests_by_date[date_key] = []
        tests_by_date[date_key].append(test)
    
    # Calculate daily averages
    daily_avg = []
    for date, day_tests in tests_by_date.items():
        avg_score = sum(t.qoe_score for t in day_tests) / len(day_tests) if day_tests else 0
        daily_avg.append({
            'date': date,
            'avg_score': avg_score,
            'test_count': len(day_tests)
        })
    
    # Sort by date
    daily_avg.sort(key=lambda x: x['date'])
    
    return render_template(
        'reports/qoe_analysis.html',
        title='QoE Analysis',
        tests=tests,
        daily_avg=daily_avg
    )


@reports_bp.route('/alerts/summary')
@login_required
def alerts_summary():
    """Alert summary report"""
    from app.models.network import Alert
    
    # Get parameters
    time_range = request.args.get('time_range', 'day')
    
    # Set time range
    if time_range == 'day':
        cutoff = datetime.utcnow() - timedelta(hours=24)
    elif time_range == 'week':
        cutoff = datetime.utcnow() - timedelta(days=7)
    elif time_range == 'month':
        cutoff = datetime.utcnow() - timedelta(days=30)
    else:
        cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # Get alerts in the time range
    alerts = Alert.query.filter(
        Alert.created_at >= cutoff
    ).order_by(Alert.created_at.desc()).all()
    
    # Count by severity
    severity_counts = {
        'low': sum(1 for a in alerts if a.severity == 'low'),
        'medium': sum(1 for a in alerts if a.severity == 'medium'),
        'high': sum(1 for a in alerts if a.severity == 'high')
    }
    
    # Count by domain
    domain_counts = {}
    for alert in alerts:
        element = NetworkElement.query.get(alert.element_id)
        if element:
            domain = element.domain
            if domain not in domain_counts:
                domain_counts[domain] = 0
            domain_counts[domain] += 1
    
    # Count acknowledged vs unacknowledged
    ack_counts = {
        'acknowledged': sum(1 for a in alerts if a.acknowledged),
        'unacknowledged': sum(1 for a in alerts if not a.acknowledged)
    }
    
    return render_template(
        'reports/alerts_summary.html',
        title='Alerts Summary',
        time_range=time_range,
        alerts=alerts,
        severity_counts=severity_counts,
        domain_counts=domain_counts,
        ack_counts=ack_counts,
        total_count=len(alerts)
    )


@reports_bp.route('/export/kpi', methods=['GET'])
@login_required
def export_kpi_data():
    """Export KPI data to CSV"""
    # Get parameters
    domain = request.args.get('domain')
    kpi_code = request.args.get('kpi_code')
    time_range = request.args.get('time_range', 'day')
    
    # Set time range
    if time_range == 'day':
        cutoff = datetime.utcnow() - timedelta(hours=24)
    elif time_range == 'week':
        cutoff = datetime.utcnow() - timedelta(days=7)
    elif time_range == 'month':
        cutoff = datetime.utcnow() - timedelta(days=30)
    else:
        cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # Start query
    query = KPIMeasurement.query.join(KPIDefinition).join(NetworkElement).filter(
        KPIMeasurement.timestamp >= cutoff
    )
    
    # Apply filters
    if domain:
        query = query.filter(NetworkElement.domain == domain)
    
    if kpi_code:
        query = query.filter(KPIDefinition.kpi_code == kpi_code)
    
    # Get measurements
    measurements = query.order_by(KPIMeasurement.timestamp).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['timestamp', 'element_name', 'domain', 'kpi_name', 'kpi_code', 'value', 'unit', 'quality_score'])
    
    # Write data
    for m in measurements:
        element = NetworkElement.query.get(m.element_id)
        kpi = KPIDefinition.query.get(m.kpi_id)
        
        writer.writerow([
            m.timestamp.isoformat(),
            element.element_name if element else '',
            element.domain if element else '',
            kpi.kpi_name if kpi else '',
            kpi.kpi_code if kpi else '',
            m.value,
            kpi.unit if kpi else '',
            m.quality_score
        ])
    
    # Prepare response
    output.seek(0)
    filename = f"kpi_data_{time_range}_{domain or 'all'}_{kpi_code or 'all'}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        download_name=filename,
        as_attachment=True
    )


@reports_bp.route('/export/chart/<chart_type>', methods=['GET'])
@login_required
def export_chart(chart_type):
    """Generate and export chart images"""
    # Get parameters
    domain = request.args.get('domain')
    time_range = request.args.get('time_range', 'day')
    
    # Set time range
    if time_range == 'day':
        cutoff = datetime.utcnow() - timedelta(hours=24)
        date_format = '%H:%M'
    elif time_range == 'week':
        cutoff = datetime.utcnow() - timedelta(days=7)
        date_format = '%a'
    elif time_range == 'month':
        cutoff = datetime.utcnow() - timedelta(days=30)
        date_format = '%d/%m'
    else:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        date_format = '%H:%M'
    
    plt.figure(figsize=(10, 6))
    
    if chart_type == 'domain_health':
        # Domain health bar chart
        domains = ['ran', 'transport', 'core', 'internet']
        health_values = []
        
        for d in domains:
            # Count active vs total
            total = NetworkElement.query.filter_by(domain=d).count()
            active = NetworkElement.query.filter_by(domain=d, status='active').count()
            health = int((active / total * 100) if total > 0 else 0)
            health_values.append(health)
        
        # Set colors based on health values
        colors = ['#e74c3c' if h < 60 else '#f1c40f' if h < 90 else '#2ecc71' for h in health_values]
        
        plt.bar(domains, health_values, color=colors)
        plt.xlabel('Network Domain')
        plt.ylabel('Health (%)')
        plt.title(f'Domain Health Overview - {time_range.capitalize()}')
        plt.ylim(0, 100)
        
        # Add value labels on top of bars
        for i, v in enumerate(health_values):
            plt.text(i, v + 2, f"{v}%", ha='center')
        
        chart_title = f"domain_health_{time_range}_{datetime.now().strftime('%Y%m%d')}"
        
    elif chart_type == 'qoe_trend':
        # QoE trend line chart
        tests = PerformanceTest.query.filter(
            PerformanceTest.timestamp >= cutoff
        ).order_by(PerformanceTest.timestamp).all()
        
        # Group by date/hour
        data = {}
        for test in tests:
            key = test.timestamp.strftime(date_format)
            if key not in data:
                data[key] = []
            data[key].append(test.qoe_score)
        
        # Calculate averages
        x = list(data.keys())
        y = [sum(scores) / len(scores) if scores else 0 for scores in data.values()]
        
        plt.plot(x, y, marker='o', linestyle='-', color='#3498db')
        plt.xlabel('Time')
        plt.ylabel('Average QoE Score')
        plt.title(f'QoE Score Trend - {time_range.capitalize()}')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        chart_title = f"qoe_trend_{time_range}_{datetime.now().strftime('%Y%m%d')}"
        
    else:
        return jsonify({'error': 'Invalid chart type'}), 400
    
    # Save chart to memory
    img_data = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_data, format='png', dpi=100)
    img_data.seek(0)
    
    return send_file(
        img_data,
        mimetype='image/png',
        download_name=f"{chart_title}.png",
        as_attachment=True
    )
