from flask import Blueprint, render_template
from flask_login import login_required

technical_deep_dive_bp = Blueprint('technical_deep_dive', __name__)

@technical_deep_dive_bp.route('/technical-deep-dive')
@login_required
def technical_deep_dive():
    """Renders the Technical Deep Dive page."""
    return render_template('feature04/technical_deep_dive.html', title='Technical Deep Dive')
