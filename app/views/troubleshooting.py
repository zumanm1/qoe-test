from flask import Blueprint, render_template
from flask_login import login_required

troubleshooting_bp = Blueprint('troubleshooting', __name__)

@troubleshooting_bp.route('/')
@login_required
def index():
    """Renders the troubleshooting guide page."""
    return render_template('troubleshooting.html', title='Troubleshooting Guide')
