import click
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User
from app.models.network import NetworkElement, KPIDefinition
from datetime import datetime

def register_commands(app):
    """Register Click commands for the application."""
    
    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin(username, email, password):
        """Create an admin user."""
        user = User.query.filter_by(username=username).first()
        if user is not None:
            click.echo('Error: Admin user already exists.')
            return
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin user {username} created successfully.')
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database with required tables."""
        db.create_all()
        click.echo('Database initialized.')
        
    @app.cli.command('setup-all')
    @click.option('--admin-username', default='admin', help='Admin username')
    @click.option('--admin-email', default='admin@mtn.com', help='Admin email')
    @click.option('--admin-password', default='ChangeMeNow!', help='Admin password')
    def setup_all(admin_username, admin_email, admin_password):
        """Set up everything: Initialize DB, run migrations, seed data, create admin."""
        click.echo('Setting up Mobile Network QoE Tool...')
        
        # Initialize database
        click.echo('\nInitializing database...')
        db.create_all()
        
        # Create admin user
        click.echo('\nCreating admin user...')
        user = User.query.filter_by(username=admin_username).first()
        if user is None:
            user = User(
                username=admin_username,
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                role='admin',
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            click.echo(f'Admin user {admin_username} created successfully.')
        else:
            click.echo('Admin user already exists.')
        
        # Run KPI seeding
        click.echo('\nSeeding KPI definitions...')
        seed_kpis()
        
        # Run network element seeding
        click.echo('\nSeeding network elements...')
        seed_network()
        
        click.echo('\n✅ Mobile Network QoE Tool setup completed successfully!')
        click.echo(f'You can now log in with username: {admin_username} and the provided password.')
    
    @app.cli.command('seed-kpis')
    def seed_kpis():
        """Seed the database with KPI definitions."""
        kpi_data = [
            # RAN KPIs
            {
                'kpi_name': 'Signal-to-Interference-plus-Noise Ratio',
                'kpi_code': 'sinr',
                'unit': 'dB',
                'domain': 'ran',
                'impact_level': 'high',
                'min_value': -5,
                'max_value': 30,
                'optimal_value': 20,
                'description': 'Measures the ratio of the received desired signal to the received undesired signals (interference and noise).'
            },
            {
                'kpi_name': 'Physical Resource Block Utilization',
                'kpi_code': 'prb_util',
                'unit': '%',
                'domain': 'ran',
                'impact_level': 'medium',
                'min_value': 0,
                'max_value': 100,
                'optimal_value': 50,
                'description': 'Percentage of allocated PRBs relative to the total available PRBs.'
            },
            {
                'kpi_name': 'Block Error Rate',
                'kpi_code': 'bler',
                'unit': '%',
                'domain': 'ran',
                'impact_level': 'high',
                'min_value': 0,
                'max_value': 30,
                'optimal_value': 2,
                'description': 'Ratio of the number of erroneous blocks to the total number of blocks.'
            },
            
            # Transport KPIs
            {
                'kpi_name': 'MPLS Tunnel Utilization',
                'kpi_code': 'mpls_util',
                'unit': '%',
                'domain': 'transport',
                'impact_level': 'high',
                'min_value': 0,
                'max_value': 100,
                'optimal_value': 60,
                'description': 'Percentage utilization of MPLS tunnels in the transport network.'
            },
            {
                'kpi_name': 'LSP Flapping Rate',
                'kpi_code': 'lsp_flapping',
                'unit': 'events/hr',
                'domain': 'transport',
                'impact_level': 'high',
                'min_value': 0,
                'max_value': 10,
                'optimal_value': 0,
                'description': 'Number of Label Switched Path state changes per hour.'
            },
            
            # Core KPIs
            {
                'kpi_name': 'GTP-U Tunnel Efficiency',
                'kpi_code': 'gtp_efficiency',
                'unit': '%',
                'domain': 'core',
                'impact_level': 'medium',
                'min_value': 70,
                'max_value': 100,
                'optimal_value': 95,
                'description': 'Efficiency of GTP tunnels in handling user data packets.'
            },
            {
                'kpi_name': 'Bearer QoS Policy Rate',
                'kpi_code': 'bearer_rate',
                'unit': 'Mbps',
                'domain': 'core',
                'impact_level': 'medium',
                'min_value': 10,
                'max_value': 500,
                'optimal_value': 100,
                'description': 'Maximum bit rate allowed by QoS policy for user bearers.'
            },
            
            # End-to-End KPIs
            {
                'kpi_name': 'Download Speed',
                'kpi_code': 'dl_speed',
                'unit': 'Mbps',
                'domain': 'e2e',
                'impact_level': 'high',
                'min_value': 1,
                'max_value': 1000,
                'optimal_value': 50,
                'description': 'Measured download speed from speed test.'
            },
            {
                'kpi_name': 'Upload Speed',
                'kpi_code': 'ul_speed',
                'unit': 'Mbps',
                'domain': 'e2e',
                'impact_level': 'high',
                'min_value': 1,
                'max_value': 500,
                'optimal_value': 25,
                'description': 'Measured upload speed from speed test.'
            },
            {
                'kpi_name': 'Latency',
                'kpi_code': 'latency',
                'unit': 'ms',
                'domain': 'e2e',
                'impact_level': 'high',
                'min_value': 5,
                'max_value': 500,
                'optimal_value': 20,
                'description': 'End-to-end round-trip time for packets.'
            },
            {
                'kpi_name': 'Jitter',
                'kpi_code': 'jitter',
                'unit': 'ms',
                'domain': 'e2e',
                'impact_level': 'medium',
                'min_value': 0,
                'max_value': 100,
                'optimal_value': 5,
                'description': 'Variation in packet delay.'
            },
            {
                'kpi_name': 'Packet Loss',
                'kpi_code': 'packet_loss',
                'unit': '%',
                'domain': 'e2e',
                'impact_level': 'high',
                'min_value': 0,
                'max_value': 30,
                'optimal_value': 0,
                'description': 'Percentage of packets that fail to reach their destination.'
            },
            {
                'kpi_name': 'QoE Score',
                'kpi_code': 'qoe_score',
                'unit': '',
                'domain': 'e2e',
                'impact_level': 'high',
                'min_value': 0,
                'max_value': 100,
                'optimal_value': 90,
                'description': 'Calculated Quality of Experience score.'
            }
        ]
        
        # Add KPI definitions to the database
        for kpi in kpi_data:
            existing = KPIDefinition.query.filter_by(kpi_code=kpi['kpi_code']).first()
            if existing is None:
                kpi_def = KPIDefinition(**kpi)
                db.session.add(kpi_def)
        
        db.session.commit()
        click.echo('KPI definitions seeded successfully.')
    
    @app.cli.command('seed-network')
    def seed_network():
        """Seed the database with sample network elements."""
        network_elements = [
            # RAN elements
            {
                'element_name': 'UE_DEVICE',
                'element_type': 'mobile',
                'domain': 'ran',
                'protocol_layer': 'l1',
                'location': 'Client Side',
                'status': 'active'
            },
            {
                'element_name': 'ENB_SITE_1',
                'element_type': 'enb',
                'domain': 'ran',
                'protocol_layer': 'l1-l3',
                'location': 'Cell Site Alpha',
                'status': 'active'
            },
            
            # Transport elements
            {
                'element_name': 'ROUTER_EDGE_1',
                'element_type': 'router',
                'domain': 'transport',
                'protocol_layer': 'l3',
                'location': 'Edge POP 1',
                'status': 'active'
            },
            {
                'element_name': 'MPLS_P_1',
                'element_type': 'router',
                'domain': 'transport',
                'protocol_layer': 'l2-l3',
                'location': 'Core Network',
                'status': 'active'
            },
            
            # Core elements
            {
                'element_name': 'S_GW_1',
                'element_type': 'gateway',
                'domain': 'core',
                'protocol_layer': 'l3-l4',
                'location': 'Core Data Center',
                'status': 'active'
            },
            {
                'element_name': 'P_GW_1',
                'element_type': 'gateway',
                'domain': 'core',
                'protocol_layer': 'l3-l4',
                'location': 'Core Data Center',
                'status': 'active'
            },
            
            # Internet elements
            {
                'element_name': 'INTERNET_GW',
                'element_type': 'gateway',
                'domain': 'internet',
                'protocol_layer': 'l3',
                'location': 'Internet Edge',
                'status': 'active'
            },
            {
                'element_name': 'SPEEDTEST_SERVER',
                'element_type': 'server',
                'domain': 'internet',
                'protocol_layer': 'l7',
                'location': 'Data Center',
                'status': 'active'
            }
        ]
        
        # Add network elements to the database
        for element in network_elements:
            existing = NetworkElement.query.filter_by(element_name=element['element_name']).first()
            if existing is None:
                net_elem = NetworkElement(**element)
                db.session.add(net_elem)
        
        db.session.commit()
        click.echo('Network elements seeded successfully.')
    
    @app.cli.command('clean-db')
    @click.confirmation_option(prompt='Are you sure you want to drop all tables? This will delete ALL data!')
    def clean_db():
        """Drop all tables and remove all data."""
        db.drop_all()
        click.echo('Database cleared - all tables dropped.')
