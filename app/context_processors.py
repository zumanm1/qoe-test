import datetime

def inject_current_year():
    """Inject the current year and now() function into the template context."""
    return {
        'current_year': datetime.datetime.now().year,
        'now': datetime.datetime.now
    }
