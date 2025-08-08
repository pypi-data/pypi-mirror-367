"""Django .gitignore template."""

DJANGO_TEMPLATE = {
    'name': 'Django',
    'content': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Media and static files
/media
/static
staticfiles/

# Virtual environment
venv/
env/
.venv/

# Environment variables
.env
.env.local

# Database
*.db

# Session files
django_session

# Celery
celerybeat-schedule
celerybeat.pid

# Coverage
htmlcov/
.coverage
.coverage.*

# Translations
*.mo
*.pot

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
Thumbs.db'''
}