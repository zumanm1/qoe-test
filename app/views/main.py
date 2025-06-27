from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the index page."""
    return render_template('index.html')

@main_bp.route('/home')
def home():
    """Redirect to index."""
    return redirect(url_for('main.index'))
