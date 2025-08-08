# fenix/extensions/__init__.py
from fenix.extensions.middleware import auth

def init_extensions(app):
    app.auth_required = auth.auth_required
    print("✅ Extensions initialized")
