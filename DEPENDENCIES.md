# Key Dependencies

This document provides an overview of the key dependencies used in the QoE Tool project and the rationale for their selection.

## Backend Dependencies (Python/Flask)

### Core Web Framework
- **Flask** (3.1.1)
  - Primary web framework for the application
  - Chosen for its simplicity, flexibility, and extensive ecosystem
  - Provides routing, templating, and HTTP request handling

### Database & ORM
- **SQLAlchemy** (2.0.41)
  - Object-Relational Mapping (ORM) for database operations
  - Provides database-agnostic abstraction layer
  - Enables complex queries and relationships management
- **Flask-SQLAlchemy** (3.1.1)
  - Flask integration for SQLAlchemy
  - Simplifies configuration and initialization
- **Flask-Migrate** (4.1.0)
  - Database schema migrations using Alembic
  - Version control for database structure changes
  - Essential for production deployments

### Authentication & Security
- **Flask-Login** (0.6.3)
  - User session management and authentication
  - Provides login/logout functionality and user state tracking
  - Integrates seamlessly with Flask applications
- **bcrypt** (4.3.0)
  - Password hashing and verification
  - Industry-standard cryptographic security for user passwords
- **cryptography** (44.0.3)
  - Additional cryptographic primitives and protocols

### Real-time Communication
- **Flask-SocketIO** (5.5.1)
  - WebSocket support for real-time features
  - Enables live updates for simulation progress and network monitoring
  - Critical for interactive dashboard functionality
- **python-socketio** (5.13.0)
  - Core Socket.IO implementation for Python
- **eventlet** (0.39.1)
  - Concurrent networking library for Socket.IO server

### Data Science & Simulation Engine
- **NumPy** (2.3.1)
  - Fundamental package for numerical computing
  - Powers mathematical calculations in QoE simulations
  - Foundation for other scientific libraries
- **SciPy** (1.16.0)
  - Scientific computing library for advanced mathematical functions
  - Used for statistical analysis and optimization algorithms
- **scikit-learn** (1.7.0)
  - Machine learning algorithms for QoE prediction models
  - Provides regression, classification, and clustering capabilities
- **pandas** (2.3.0)
  - Data manipulation and analysis
  - Handles time-series data and performance metrics
- **matplotlib** (3.10.3) & **seaborn** (0.13.2)
  - Data visualization libraries for generating charts and reports

### Network Management
- **netmiko** (4.5.0)
  - Multi-vendor network device connectivity
  - SSH connections to routers, switches, and network equipment
- **napalm** (5.0.0)
  - Network device automation and configuration management
  - Vendor-agnostic network programming interface
- **paramiko** (3.5.1)
  - SSH2 protocol library for secure connections
- **ncclient** (0.6.15)
  - NETCONF client for network configuration management

### Web Testing & Automation
- **selenium** (4.33.0)
  - Web browser automation for end-to-end testing
  - Simulates user interactions for QoE measurements
- **pyshark** (0.6)
  - Python wrapper for tshark (Wireshark)
  - Network packet capture and analysis

### API & HTTP
- **Flask-RESTful** (0.3.10)
  - REST API development framework
  - Simplifies creation of RESTful web services
- **requests** (2.31.0)
  - HTTP library for external API calls
- **Flask-CORS** (6.0.1)
  - Cross-Origin Resource Sharing support

### Development & Testing
- **pytest** (7.4.0)
  - Testing framework for unit and integration tests
- **pytest-cov** (4.1.0)
  - Test coverage reporting
- **black** (23.7.0)
  - Code formatting tool for consistent Python style
- **flake8** (6.0.0)
  - Code linting and style checking

## Frontend Dependencies (JavaScript/Node.js)

### Testing Framework
- **Jest** (29.7.0)
  - JavaScript testing framework for unit and integration tests
  - Chosen for its comprehensive testing capabilities and built-in mocking
- **Puppeteer** (24.11.0)
  - Headless Chrome browser automation
  - Enables end-to-end testing of web application functionality
  - Provides programmatic control over browser interactions

### CSS Framework
- **Bootstrap** (5.1.3) - *CDN*
  - Responsive CSS framework for rapid UI development
  - Provides consistent styling and responsive grid system
  - Extensive component library reduces development time

### JavaScript Libraries (CDN)
- **Chart.js** (3.7.0)
  - Interactive data visualization library
  - Creates responsive charts for QoE metrics and performance data
  - Lightweight and highly customizable
- **Socket.IO** (4.4.1)
  - Real-time bidirectional event-based communication
  - Client-side counterpart to Flask-SocketIO
  - Enables live dashboard updates and notifications
- **jQuery** (3.6.0)
  - JavaScript library for DOM manipulation
  - Simplifies AJAX requests and event handling
  - Still widely used for legacy compatibility

### Icons & Fonts
- **Font Awesome** (6.0.0) - *CDN*
  - Comprehensive icon library
  - Provides scalable vector icons for UI elements

## Production Dependencies

### Web Server
- **Gunicorn** (21.2.0)
  - Python WSGI HTTP Server for UNIX
  - Production-grade web server for serving Flask applications
  - Better performance and stability than development server

### Process Management
- **APScheduler** (3.11.0)
  - Advanced Python Scheduler for background tasks
  - Handles periodic network monitoring and data collection

### Data Storage
- **redis** (4.6.0)
  - In-memory data structure store
  - Used for caching and session storage
  - Improves application performance

## Deployment & Configuration

### Environment Management
- **python-dotenv** (1.0.0)
  - Loads environment variables from .env files
  - Simplifies configuration management across environments

### Documentation
- **setuptools** (80.9.0)
  - Python package installation and distribution
  - Required for proper package management

## Rationale for Key Technology Choices

### Flask vs. Django
- **Flask** was chosen over Django for its:
  - Lightweight and modular architecture
  - Flexibility in choosing components
  - Better suited for API-heavy applications
  - Easier integration with scientific Python libraries

### SQLAlchemy vs. Django ORM
- **SQLAlchemy** provides:
  - More powerful query capabilities
  - Better performance for complex operations
  - Database-agnostic approach
  - Explicit control over database operations

### Chart.js vs. D3.js
- **Chart.js** was selected because:
  - Simpler API for common chart types
  - Built-in responsive design
  - Smaller learning curve
  - Good performance for real-time updates

### Socket.IO vs. WebSockets
- **Socket.IO** offers:
  - Automatic fallback mechanisms
  - Built-in room and namespace support
  - Better browser compatibility
  - Simplified real-time communication

### NumPy/SciPy/Sklearn vs. R
- **Python scientific stack** chosen for:
  - Seamless integration with web framework
  - Single language across the entire application
  - Extensive machine learning libraries
  - Better deployment options for web applications

### Puppeteer vs. Selenium
- **Puppeteer** used for:
  - Better performance with headless Chrome
  - More reliable for modern web applications
  - Simpler API for Chrome-specific testing
- **Selenium** retained for:
  - Multi-browser testing capabilities
  - Legacy test suite compatibility
