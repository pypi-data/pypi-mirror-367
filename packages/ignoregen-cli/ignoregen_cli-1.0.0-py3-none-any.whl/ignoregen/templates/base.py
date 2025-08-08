"""Base .gitignore template."""

BASE_TEMPLATE = {
    'name': 'Base',
    'content': '''# IDEs and editors
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log

# Environment variables
.env
.env.local

# Build outputs
build/
dist/
out/'''
}