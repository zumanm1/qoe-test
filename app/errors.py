from flask import render_template, jsonify, request

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Bad Request',
                'message': str(error)
            }), 400
        return render_template('errors/400.html', title='Bad Request'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource'
            }), 401
        return render_template('errors/401.html', title='Unauthorized'), 401

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'The server encountered an unexpected condition'
            }), 500
        return render_template('errors/500.html', title='Server Error'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error(f'Unhandled Exception: {error}', exc_info=True)
        if request.path.startswith('/api'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html', title='Unexpected Error'), 500
