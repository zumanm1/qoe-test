import os
from app import create_app, db, socketio
from app.models.user import User
from app.models.network import NetworkElement, KPIDefinition
from app.models.simulation import SimulationScenario
from flask_migrate import Migrate
from app.cli import register_commands

# Create app instance using environment variable or default to development
app = create_app(os.getenv('FLASK_ENV', 'development'))
migrate = Migrate(app, db)

# Register CLI commands
register_commands(app)

# Define Flask shell context
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'NetworkElement': NetworkElement,
        'KPIDefinition': KPIDefinition,
        'SimulationScenario': SimulationScenario
    }

if __name__ == '__main__':
    # Use socketio.run() to support WebSockets and enable debug mode for development
    socketio.run(app, debug=True)
