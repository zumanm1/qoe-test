# Mobile QoE Tool - Architecture Overview

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Architecture](#data-architecture)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [API Architecture](#api-architecture)
8. [Real-time Communication](#real-time-communication)
9. [Performance Considerations](#performance-considerations)
10. [Development Workflow](#development-workflow)
11. [Technology Stack](#technology-stack)
12. [Integration Points](#integration-points)

---

## System Overview

The Mobile QoE Tool is a comprehensive web application designed to monitor, simulate, and optimize network Quality of Experience (QoE) across mobile network infrastructure. The system provides real-time monitoring, interactive network topology visualization, QoE simulation capabilities, and comprehensive reporting for network engineers and operations teams.

### Core Objectives
- **Real-time Network Monitoring**: Centralized monitoring across RAN, Transport, and Core domains
- **QoE Simulation**: Predictive modeling of network parameter changes
- **Automated Diagnostics**: Intelligent troubleshooting and optimization recommendations
- **Executive Visibility**: High-level dashboards and comprehensive reporting

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser Client (HTML5, CSS3, JavaScript, Bootstrap 5)     │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ Dashboard   │ │ Simulation  │ │  Reports    │ │    API      ││
│  │   Views     │ │    Views    │ │   Views     │ │  Interface  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                         ┌──────▼──────┐
                         │  Load       │
                         │ Balancer    │
                         │ (Nginx)     │
                         └──────┬──────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                    Flask Web Application                        │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │    Auth     │ │ Dashboard   │ │ Simulation  │ │   Reports   ││
│  │  Blueprint  │ │  Blueprint  │ │  Blueprint  │ │  Blueprint  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │     API     │ │Troubleshoot │ │ QoE Impact  │ │    Docs     ││
│  │  Blueprint  │ │  Blueprint  │ │  Blueprint  │ │  Blueprint  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Business Logic Layer                           ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          ││
│  │  │   Services  │ │ Simulation  │ │   Report    │          ││
│  │  │   Layer     │ │   Engine    │ │  Generator  │          ││
│  │  └─────────────┘ └─────────────┘ └─────────────┘          ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ PostgreSQL  │ │    Redis    │ │  File       │ │   Cache     ││
│  │  Database   │ │   Cache     │ │  Storage    │ │   Layer     ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Layers

1. **Presentation Layer**: Web browser interface with responsive design
2. **Application Layer**: Flask-based web application with modular blueprints
3. **Business Logic Layer**: Core application services and processing engines
4. **Data Layer**: Persistent storage, caching, and data management

---

## Component Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │  Authentication │    │    Session      │
│   Factory       │◄──►│     Manager     │◄──►│   Management    │
│   (app.create)  │    │  (Flask-Login)  │    │   (Sessions)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Blueprint     │    │    Database     │    │     Cache       │
│   Registry      │◄──►│     Layer       │◄──►│    Manager      │
│                 │    │ (SQLAlchemy)    │    │    (Redis)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Real-time     │    │   Background    │    │   Error         │
│ Communication   │    │     Tasks       │    │   Handling      │
│ (WebSockets)    │    │   (Celery)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Blueprint Architecture

Each functional area is organized as a Flask Blueprint:

```
app/views/
├── auth.py              # Authentication & user management
├── dashboard.py         # Main monitoring dashboard
├── simulation.py        # QoE simulation engine
├── reports.py           # Report generation & analytics
├── api.py              # REST API endpoints
├── troubleshooting.py   # Diagnostic tools
├── qoe_impact.py       # QoE impact analysis
├── technical_deep_dive.py # Technical analysis views
├── docs.py             # Documentation views
└── main.py             # Core application routes
```

### Service Layer Architecture

```
app/services/
├── network_service.py      # Network element management
├── kpi_service.py          # KPI data processing
├── simulation_service.py   # QoE simulation logic
├── report_service.py       # Report generation
├── alert_service.py        # Alert management
└── analytics_service.py    # Data analysis
```

---

## Data Architecture

### Entity Relationship Model

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Users      │    │ NetworkElements │    │ KPIDefinitions  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • id (PK)       │    │ • id (PK)       │    │ • id (PK)       │
│ • username      │    │ • element_name  │    │ • kpi_name      │
│ • email         │    │ • element_type  │    │ • kpi_code      │
│ • password_hash │    │ • domain        │    │ • unit          │
│ • role          │    │ • subdomain     │    │ • domain        │
│ • is_active     │    │ • protocol_layer│    │ • impact_level  │
│ • created_at    │    │ • location      │    │ • min_value     │
│ • last_login    │    │ • status        │    │ • max_value     │
└─────────────────┘    └─────────────────┘    │ • optimal_value │
                                              │ • description   │
                                              └─────────────────┘
                                                       │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ KPIMeasurements │    │     Alerts      │    │   Subdomains    │    │   Simulations   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • id (PK)       │    │ • id (PK)       │    │ • id (PK)       │    │ • id (PK)       │
│ • element_id(FK)│    │ • element_id(FK)│    │ • name          │    │ • name          │
│ • kpi_id (FK)   │    │ • kpi_id (FK)   │    │ • domain        │    │ • parameters    │
│ • value         │    │ • alert_type    │    │ • description   │    │ • results       │
│ • timestamp     │    │ • severity      │    │ • weight        │    │ • created_at    │
│ • quality_score │    │ • message       │    │ • qoe_weight    │    │ • user_id (FK)  │
└─────────────────┘    │ • created_at    │    │ • kpi_mappings  │    └─────────────────┘
                       │ • acknowledged  │    └─────────────────┘
                       │ • acknowledged_by│
                       │ • acknowledged_at│
                       └─────────────────┘
```

### Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Data Ingestion│    │   Data Storage  │
│                 │    │                 │    │                 │
│ • Network Mgmt  │───►│ • REST APIs     │───►│ • PostgreSQL DB │
│   Systems       │    │ • File Uploads  │    │ • Time Series   │
│ • SNMP Monitors │    │ • WebSockets    │    │   Tables        │
│ • Log Files     │    │ • Batch Imports │    │ • Indexed KPIs  │
│ • External APIs │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Analytics │    │ Data Processing │    │   Data Cache    │
│                 │    │                 │    │                 │
│ • QoE Scoring   │◄───│ • Aggregations  │◄───│ • Redis Cache   │
│ • Trend Analysis│    │ • Calculations  │    │ • Session Data  │
│ • Correlations  │    │ • Transformations│    │ • Real-time     │
│ • Predictions   │    │ • Validations   │    │   Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Login    │    │  Password Hash  │    │  Session Token  │
│                 │───►│   Verification  │───►│   Generation    │
│ • Username/Email│    │ • Werkzeug      │    │ • Flask-Login   │
│ • Password      │    │   Security      │    │ • Secure Cookie │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                             │
         ▼                                             ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Role-Based    │    │    Session      │    │   CSRF Token    │
│  Authorization  │    │   Management    │    │   Protection    │
│                 │    │                 │    │                 │
│ • Admin         │    │ • 24hr Timeout  │    │ • WTF-CSRF      │
│ • Engineer      │    │ • Secure Flags  │    │ • Form Tokens   │
│ • Viewer        │    │ • HttpOnly      │    │ • AJAX Headers  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Security Layers

1. **Transport Security**: HTTPS/TLS encryption for all communications
2. **Authentication**: Password hashing with Werkzeug security
3. **Authorization**: Role-based access control (RBAC)
4. **Session Security**: Secure, HttpOnly cookies with CSRF protection
5. **Input Validation**: Server-side validation and sanitization
6. **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

### Security Configuration

```python
# config.py - Security Settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
REMEMBER_COOKIE_SECURE = True
REMEMBER_COOKIE_HTTPONLY = True
```

---

## Deployment Architecture

### Containerized Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Environment                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │    Nginx    │  │    Flask    │  │ PostgreSQL  │  │  Redis  │ │
│  │ (Reverse    │  │    App      │  │  Database   │  │ Cache   │ │
│  │  Proxy)     │  │ (Gunicorn)  │  │             │  │         │ │
│  │             │  │             │  │             │  │         │ │
│  │ Port: 80    │  │ Port: 5000  │  │ Port: 5432  │  │Port:6379│ │
│  │      443    │  │             │  │             │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│         │                │                │               │     │
│         └────────────────┼────────────────┼───────────────┘     │
│                          │                │                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Docker Network                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Persistent Volumes                         │ │
│  │  • postgres_data                                           │ │
│  │  • redis_data                                              │ │
│  │  • application_logs                                        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Service Configuration

#### Web Application (Flask + Gunicorn)
```yaml
web:
  build: .
  ports: ["5000:5000"]
  environment:
    - FLASK_ENV=production
    - DATABASE_URL=postgresql://qoe_user:qoe_password@db:5432/qoe_tool
    - REDIS_URL=redis://redis:6379/0
    - WORKERS=4
  depends_on: [db, redis]
```

#### Database (PostgreSQL)
```yaml
db:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=qoe_tool
    - POSTGRES_USER=qoe_user
    - POSTGRES_PASSWORD=qoe_password
  volumes: [postgres_data:/var/lib/postgresql/data]
```

#### Cache (Redis)
```yaml
redis:
  image: redis:7-alpine
  volumes: [redis_data:/data]
  command: redis-server --appendonly yes --maxmemory 256mb
```

---

## API Architecture

### REST API Design

```
Base URL: https://api.qoe-tool.com/api/v1

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Authentication│    │    Network      │    │      KPIs       │
│                 │    │   Elements      │    │                 │
│ POST /auth/login│    │ GET /elements   │    │ GET /kpis       │
│ POST /auth/logout│   │ GET /elements/{id}│  │ GET /kpis/{id}  │
│ GET  /auth/me   │    │ POST /elements  │    │ POST /kpis      │
└─────────────────┘    │ PUT /elements/{id}│  │ GET /kpis/      │
                       │ DELETE /elements │    │     measurements│
                       └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Simulations   │    │     Reports     │    │     Alerts      │
│                 │    │                 │    │                 │
│ GET /simulations│    │ GET /reports    │    │ GET /alerts     │
│ POST /simulations│   │ POST /reports   │    │ POST /alerts    │
│ GET /simulations│    │ GET /reports/   │    │ PUT /alerts/{id}│
│     /{id}       │    │     export      │    │ DELETE /alerts  │
│ DELETE /sims/{id}│   │ GET /reports/   │    │     /{id}       │
└─────────────────┘    │     {id}/pdf    │    └─────────────────┘
                       └─────────────────┘
```

### API Response Format

```json
{
  "status": "success|error",
  "message": "Human readable message",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "pages": 5
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Handling

```python
# Standard error responses
400: Bad Request - Invalid input parameters
401: Unauthorized - Authentication required
403: Forbidden - Insufficient permissions
404: Not Found - Resource not found
429: Too Many Requests - Rate limit exceeded
500: Internal Server Error - Server error
```

---

## Real-time Communication

### WebSocket Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Flask-SocketIO│    │    Background   │
│                 │◄──►│     Server      │◄──►│     Tasks       │
│ • Dashboard     │    │                 │    │                 │
│ • Simulation    │    │ • Event Routing │    │ • KPI Updates   │
│ • Monitoring    │    │ • Room Management│   │ • Alert Checks  │
└─────────────────┘    │ • Authentication│    │ • Data Sync     │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │     Redis       │
                       │   Message       │
                       │    Broker       │
                       └─────────────────┘
```

### Real-time Events

```javascript
// Client-side event handling
socket.on('kpi_update', function(data) {
    updateDashboardKPI(data.element_id, data.kpi_code, data.value);
});

socket.on('new_alert', function(data) {
    displayAlert(data.severity, data.message);
});

socket.on('simulation_result', function(data) {
    updateSimulationResults(data.qoe_score, data.metrics);
});
```

### Event Types

1. **KPI Updates**: Real-time network metric updates
2. **Alerts**: Critical system alerts and notifications
3. **Simulation Results**: Live simulation output
4. **System Status**: Health and connectivity updates
5. **User Activity**: Multi-user collaboration events

---

## Performance Considerations

### Caching Strategy

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Application    │    │   Redis Cache   │    │   Database      │
│    Cache        │    │                 │    │   Queries       │
│                 │    │ • Session Data  │    │                 │
│ • Template      │───►│ • KPI Metrics   │───►│ • Aggregations  │
│   Caching       │    │ • User Prefs    │    │ • Time Series   │
│ • Static Assets │    │ • Computed      │    │ • Relationships │
│ • Query Results │    │   Results       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Database Optimization

```sql
-- Optimized indexing strategy
CREATE INDEX idx_kpi_measurements_element_timestamp 
ON kpi_measurements(element_id, timestamp DESC);

CREATE INDEX idx_kpi_measurements_kpi_timestamp 
ON kpi_measurements(kpi_id, timestamp DESC);

CREATE INDEX idx_network_elements_domain 
ON network_elements(domain, status);
```

### Performance Metrics

- **API Response Time**: < 200ms for 95% of requests
- **Page Load Time**: < 3 seconds for dashboard
- **Real-time Latency**: < 500ms for WebSocket events
- **Concurrent Users**: Support for 100+ simultaneous users
- **Data Throughput**: 1000+ KPI measurements per second

---

## Development Workflow

### Development Environment Setup

```bash
# Local development setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database initialization
flask db upgrade
flask setup-all

# Development server
flask run --debug
```

### Testing Architecture

```
tests/
├── unit/
│   ├── test_models.py      # Model unit tests
│   ├── test_services.py    # Service layer tests
│   └── test_utils.py       # Utility function tests
├── integration/
│   ├── test_api.py         # API endpoint tests
│   ├── test_auth.py        # Authentication tests
│   └── test_simulation.py  # Simulation engine tests
├── functional/
│   ├── test_dashboard.py   # UI functionality tests
│   └── test_workflows.py   # End-to-end workflows
└── fixtures/
    ├── sample_data.py      # Test data fixtures
    └── mock_responses.py   # Mock API responses
```

### Code Quality Tools

```yaml
# pyproject.toml configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=app --cov-report=html"

[tool.flake8]
max-line-length = 88
exclude = [".git", "__pycache__", "migrations"]

[tool.black]
line-length = 88
target-version = ['py39']
```

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Flask | 2.3+ | Web application framework |
| **Database** | PostgreSQL | 15+ | Primary data storage |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Cache** | Redis | 7+ | Session & data caching |
| **WebSockets** | Flask-SocketIO | 5.3+ | Real-time communication |
| **Authentication** | Flask-Login | 0.6+ | User session management |
| **Migrations** | Flask-Migrate | 4.0+ | Database schema management |
| **Server** | Gunicorn | 20+ | WSGI application server |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **UI Framework** | Bootstrap | 5.3+ | Responsive design |
| **Charts** | Chart.js | 4.0+ | Data visualization |
| **Real-time** | Socket.IO | 4.7+ | WebSocket client |
| **HTTP Client** | Fetch API | ES6+ | API communication |
| **Module Bundler** | Webpack | 5.0+ | Asset bundling |

### DevOps & Infrastructure

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Containerization** | Docker | 24+ | Application packaging |
| **Orchestration** | Docker Compose | 2.0+ | Multi-container deployment |
| **Reverse Proxy** | Nginx | 1.24+ | Load balancing & SSL |
| **Process Manager** | systemd | - | Service management |
| **Monitoring** | Prometheus | 2.40+ | Metrics collection |

---

## Integration Points

### External System Interfaces

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Network Mgmt  │    │   SNMP Agents   │    │   Log Systems   │
│    Systems      │───►│                 │───►│                 │
│                 │    │ • Routers       │    │ • Syslog        │
│ • REST APIs     │    │ • Switches      │    │ • Application   │
│ • SOAP Services │    │ • Base Stations │    │   Logs          │
│ • File Exports  │    │ • Core Nodes    │    │ • Audit Trails  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   QoE Tool      │
                        │   Integration   │
                        │     Layer       │
                        └─────────────────┘
```

### Data Integration Patterns

1. **Real-time Streaming**: WebSocket connections for live data
2. **Batch Processing**: Scheduled imports for historical data
3. **API Polling**: Regular checks for system status updates
4. **Event-driven**: Webhook notifications for critical events
5. **File Transfer**: SFTP/FTP for bulk data exchanges

### Integration Security

- **API Keys**: Secure authentication for external services
- **OAuth 2.0**: Standard authorization for third-party integrations
- **VPN Tunnels**: Secure network connections for sensitive data
- **Certificate Authentication**: Mutual TLS for high-security interfaces
- **Rate Limiting**: Protection against abuse and overload

---

## Conclusion

This architecture overview provides a comprehensive view of the Mobile QoE Tool's design, covering all major aspects from high-level system architecture to detailed implementation considerations. The modular, scalable design ensures the system can grow with organizational needs while maintaining performance, security, and reliability standards.

### Key Architectural Principles

1. **Modularity**: Blueprint-based architecture for maintainable code
2. **Scalability**: Horizontal scaling through containerization
3. **Security**: Multi-layered security approach with RBAC
4. **Performance**: Caching strategies and optimized data access
5. **Reliability**: Health checks, monitoring, and error handling
6. **Flexibility**: Extensible design for future enhancements

### Future Considerations

- **Microservices Migration**: Potential evolution to microservices architecture
- **Machine Learning Integration**: AI-powered analytics and predictions
- **Multi-tenancy**: Support for multiple organizations
- **Global Deployment**: Geographic distribution for reduced latency
- **Mobile Applications**: Native mobile apps for field engineers

This document serves as the definitive architectural reference for developers, architects, and stakeholders working with the Mobile QoE Tool system.
