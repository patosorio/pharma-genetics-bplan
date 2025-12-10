"""Dash application integrated with FastAPI."""

import os
import dash
import dash_bootstrap_components as dbc
from starlette.middleware.wsgi import WSGIMiddleware

# Get the directory of this file
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))

# Create Dash app with proper path configuration for mounting
# Key: requests_pathname_prefix tells Dash what URL prefix it's mounted at
dash_app = dash.Dash(
    __name__,
    requests_pathname_prefix='/dashboard/',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Hi Tai Business Plan Dashboard",
    assets_folder=os.path.join(DASHBOARD_DIR, 'assets')
)

# Import layout and callbacks
from dashboard.layout import get_layout
from dashboard import callbacks  # noqa: F401

# Set layout
dash_app.layout = get_layout()


# Custom WSGI wrapper to inject SCRIPT_NAME
class WSGIApp:
    """Wrapper to set SCRIPT_NAME for proper path handling."""
    
    def __init__(self, app, script_name):
        self.app = app
        self.script_name = script_name
    
    def __call__(self, environ, start_response):
        # Set SCRIPT_NAME to tell the WSGI app its mount point
        environ['SCRIPT_NAME'] = self.script_name
        # Adjust PATH_INFO to remove the script name if it's there
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith(self.script_name):
            environ['PATH_INFO'] = path_info[len(self.script_name):]
        return self.app(environ, start_response)


# Mount Dash's Flask app onto FastAPI
def mount_dash_to_fastapi():
    """Mount the Dash app to FastAPI using WSGI middleware with proper path prefix."""
    from src.main import app as fastapi_app
    # Wrap Dash's server with our custom WSGI wrapper, then mount it
    wrapped_app = WSGIApp(dash_app.server, '/dashboard')
    fastapi_app.mount("/dashboard", WSGIMiddleware(wrapped_app))

# Execute the mounting
mount_dash_to_fastapi()

