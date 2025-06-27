import os
from flask import Blueprint, send_from_directory, current_app
from flask_login import login_required

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/download-docs')
@login_required
def download_docs():
    """Provides the documentation PDF for download."""
    docs_path = current_app.root_path
    return send_from_directory(directory=docs_path, path='MTN_QoE_Tool_Documentation.pdf', as_attachment=True)
