# Mobile QoE Tool

A comprehensive web application for monitoring and simulating network Quality of Experience (QoE).

## Features

- **QoE Simulation Engine**: Test network parameters and view their impact on Quality of Experience
- **Interactive Network Topology**: Visualize network elements and their relationships
- **Scenario Comparison**: Compare different network scenarios side-by-side
- **Real-time Monitoring**: Track network KPIs and QoE metrics in real-time
- **Reports & Analytics**: Generate and export comprehensive QoE reports

## Project Structure

```
QoE-TOOL/
├── app/                      # Main application package
│   ├── __init__.py           # Application factory
│   ├── auth/                 # Authentication blueprint
│   ├── dashboard/            # Dashboard blueprint
│   ├── simulation/           # Simulation blueprint
│   ├── reports/              # Reports blueprint
│   ├── api/                  # API blueprint
│   ├── models/               # SQLAlchemy models
│   ├── services/             # Business logic services
│   ├── static/               # Static assets (JS, CSS)
│   └── templates/            # Jinja2 templates
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── config.py                 # Configuration classes
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose services
└── README.md                 # This file
```

## Installation

### Local Development

1. Clone the repository:
```
git clone <repository-url>
cd QoE-TOOL
```

2. Set up a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set environment variables:
```
export FLASK_APP=run.py
export FLASK_DEBUG=1
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://localhost/qoe_db"
```

5. Initialize the database:
```
flask db upgrade
flask setup-all  # Creates admin, seeds KPIs and network elements
```

6. Run the application:
```
flask run
```

### Docker Deployment

1. Build and start the containers:
```
docker-compose up -d
```

2. The application will be available at http://localhost:5000

3. To initialize the database (first time only):
```
docker-compose exec web flask setup-all
```

## User Roles

- **Admin**: Full access to all features
- **Engineer**: Access to simulations, reports, and limited configuration
- **Viewer**: Read-only access to dashboards and reports

## Database Migrations

To manage database changes:

```
# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Revert migrations if needed
flask db downgrade
```

## Development

### Adding New KPIs

Add new KPI definitions to `app/cli.py` in the `seed_kpis` function, then run:

```
flask seed-kpis
```

### Seeding Network Elements

Add network elements to the `seed_network` function in `app/cli.py`, then run:

```
flask seed-network
```

## Testing

Run the test suite with:

```bash
# Run all tests
pytest

# Run with verbose output and coverage
pytest -v --cov=app

# Run specific test file
pytest test_example.py
```

For detailed testing guidance, see the [Contributor Guide](CONTRIBUTOR_GUIDE.md#testing-guide).

## 🤝 Contributing

**New contributors should start here**: [CONTRIBUTOR_GUIDE.md](CONTRIBUTOR_GUIDE.md)

This comprehensive guide provides:
- 🗺️ **Navigation tips**: Where to start (models → blueprints → services)
- 🚀 **Setup checklist**: Step-by-step development environment setup
- 🔄 **Migration workflow**: How to handle database changes safely
- 🧪 **Testing best practices**: Writing and running tests effectively
- 🐛 **Debugging tips**: Common issues and solutions
- 📚 **Documentation reference**: How this README is organized

### Quick Start for Contributors

1. **Read the models first** (`app/models/`) to understand data structure
2. **Explore blueprints** (`app/views/`) to see application logic
3. **Check the services** (`app/services/`) for business logic
4. **Run migrations** with `flask db upgrade`
5. **Run tests** with `pytest -v`
6. **Use debugging tools** like `flask shell` for interactive exploration

## License

© Mobile Group, All Rights Reserved
