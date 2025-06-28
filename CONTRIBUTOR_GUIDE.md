# Contributor Navigation Guide

Welcome to the Mobile QoE Tool project! This guide will help you navigate the codebase effectively and get started with contributions.

## 🗺️ Where to Start: Recommended Reading Order

### 1. **Start with Models** (`app/models/`)
Understanding the data structure is crucial before diving into other components:

- **`app/models/user.py`** - User authentication and role management
- **`app/models/network.py`** - Network elements, KPIs, and QoE metrics  
- **`app/models/subdomain.py`** - Domain-specific models
- **`app/models/simulation.py`** - Simulation sessions and results
- **`app/models/__init__.py`** - Model registration overview

**💡 Tip**: Models define the database schema and business entities. Understanding these first will help you comprehend the entire application flow.

### 2. **Then Explore Blueprints/Views** (`app/views/`)
After understanding the data models, explore the application logic:

- **`app/views/main.py`** - Main application routes and landing pages
- **`app/views/auth.py`** - User authentication and session management
- **`app/views/dashboard.py`** - Dashboard functionality and real-time monitoring
- **`app/views/simulation.py`** - QoE simulation engine interface
- **`app/views/reports.py`** - Report generation and analytics
- **`app/views/api.py`** - REST API endpoints for frontend integration

**💡 Tip**: Views/blueprints contain the application's business logic and user interface. They show how models are used in practice.

### 3. **Review Configuration** (`config.py`, `run.py`)
- **`config.py`** - Application configuration classes for different environments
- **`run.py`** - Application entry point and initialization
- **`app/__init__.py`** - Application factory pattern implementation

### 4. **Understand Services** (`app/services/`)
- **`app/services/simulation.py`** - Core simulation engine and algorithms
- Other service modules for complex business logic

## 🚀 Getting Started Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] PostgreSQL or SQLite for database
- [ ] Git for version control
- [ ] Virtual environment tool (venv, conda, etc.)

### Initial Setup
1. **Clone and Environment Setup**
   ```bash
   git clone <repository-url>
   cd QoE-TOOL
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   export FLASK_APP=run.py
   export FLASK_DEBUG=1
   export SECRET_KEY="your-development-secret-key"
   export DATABASE_URL="postgresql://localhost/qoe_db"  # or sqlite:///qoe.db
   ```

3. **Database Initialization**
   ```bash
   flask db upgrade
   flask setup-all  # Creates admin user and seeds initial data
   ```

4. **Verify Installation**
   ```bash
   flask run
   # Navigate to http://localhost:5000
   ```

## 🔄 Database Migrations

### Running Migrations
```bash
# Apply pending migrations
flask db upgrade

# Check migration status
flask db current

# View migration history
flask db history
```

### Creating New Migrations
When you modify models in `app/models/`:

```bash
# Generate migration after model changes
flask db migrate -m "Add new field to NetworkElement"

# Review the generated migration file in migrations/versions/
# Edit if necessary, then apply:
flask db upgrade
```

### Migration Best Practices
- **Always review** generated migration files before applying
- **Test migrations** on development data first
- **Use descriptive messages** for migration descriptions
- **Backup production data** before running migrations in production

### Common Migration Commands
```bash
# Rollback to previous migration
flask db downgrade

# Rollback to specific revision
flask db downgrade <revision_id>

# Show current migration info
flask db show

# Generate SQL for migration (don't execute)
flask db upgrade --sql
```

## 🧪 Testing Guide

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_example.py

# Run specific test class
pytest test_example.py::TestAuthentication

# Run specific test method
pytest test_example.py::TestAuthentication::test_login_page_loads

# Run with coverage report
pytest --cov=app
```

### Test Structure
Our tests are organized by functionality:
- **Authentication tests**: Login, logout, user management
- **Dashboard tests**: UI components, data display
- **Model tests**: Database operations, data validation  
- **API tests**: REST endpoints, JSON responses
- **Performance tests**: Query performance, load testing

### Writing New Tests
Follow the existing patterns in `test_example.py`:

```python
class TestYourFeature:
    """Test suite for your new feature."""
    
    def test_specific_functionality(self, client, authenticated_user):
        """Test description."""
        # Arrange
        # Act
        # Assert
```

## 🐛 Debugging Tips

### Common Issues and Solutions

1. **Database Connection Errors**
   ```bash
   # Check database URL configuration
   echo $DATABASE_URL
   
   # Test database connection
   flask shell
   >>> from app import db
   >>> db.engine.execute('SELECT 1')
   ```

2. **Migration Errors**
   ```bash
   # Check current migration state
   flask db current
   
   # If migrations are out of sync, try:
   flask db stamp head  # Mark as current (be careful!)
   ```

3. **Import Errors**
   - Ensure `FLASK_APP=run.py` is set
   - Check `app/__init__.py` for proper imports
   - Verify virtual environment is activated

4. **Template Not Found Errors**
   - Check template file names and paths in `app/templates/`
   - Verify blueprint template folder configurations

### Debugging Tools
- **Flask Debug Mode**: Set `FLASK_DEBUG=1` for detailed error pages
- **SQLAlchemy Echo**: Add `SQLALCHEMY_ECHO=True` to see all SQL queries
- **Python Debugger**: Use `import pdb; pdb.set_trace()` for breakpoints
- **Flask Shell**: `flask shell` for interactive Python session with app context

### Logging
```python
import logging
app.logger.info("Debug message")
app.logger.error("Error occurred", exc_info=True)
```

## 📚 README Sections Reference

The main [README.md](README.md) contains essential information organized into these key sections:

### 🏗️ Project Structure
- **Overview**: Complete directory structure explanation
- **Component Organization**: How blueprints, models, and services are organized

### ⚙️ Installation 
- **Local Development**: Step-by-step setup for development environment
- **Docker Deployment**: Container-based deployment instructions
- **Environment Variables**: Required configuration settings

### 👥 User Roles
- **Admin**: Full system access and configuration
- **Engineer**: Simulation and analysis capabilities  
- **Viewer**: Read-only dashboard and report access

### 🛠️ Development
- **Adding New KPIs**: How to extend the KPI system
- **Seeding Network Elements**: Populating initial network data
- **CLI Commands**: Available Flask CLI commands

## 🎯 Development Workflow

### For New Features
1. **Understand the requirement** by reviewing existing similar features
2. **Design the model** if database changes are needed
3. **Create/update models** in `app/models/`
4. **Generate migration** with `flask db migrate`
5. **Implement business logic** in `app/services/`
6. **Create views/routes** in appropriate blueprint
7. **Add templates** if UI changes are needed
8. **Write tests** for new functionality
9. **Update documentation** as needed

### For Bug Fixes
1. **Reproduce the issue** in development environment
2. **Write a failing test** that demonstrates the bug
3. **Implement the fix**
4. **Verify the test passes**
5. **Check for regression** by running full test suite

## 📝 Code Style Guidelines

- **Follow PEP 8** for Python code formatting
- **Use descriptive variable names** and function names
- **Add docstrings** to all functions and classes
- **Write comments** for complex business logic
- **Use type hints** where appropriate
- **Keep functions small** and focused on single responsibility

## 🔗 Key Dependencies

Understanding these will help you navigate the codebase:

- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Pytest**: Testing framework
- **Bootstrap**: Frontend UI framework

## 🤝 Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Follow the development workflow** outlined above
3. **Ensure all tests pass** before submitting
4. **Update documentation** for any user-facing changes
5. **Submit a pull request** with clear description of changes

## 🆘 Getting Help

- **Check the README** for basic setup and usage
- **Review test examples** for implementation patterns
- **Examine existing code** for similar functionality
- **Use Flask shell** for interactive debugging
- **Check Flask and SQLAlchemy docs** for framework-specific questions

---

**Happy coding! 🚀**

*This guide is a living document. Please update it as the project evolves.*
