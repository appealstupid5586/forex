import os

# Make `app` a thin package that points into `backend/app` so legacy imports
# like `import app.strategy` continue to work during migration.
__path__.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))
