"""React .gitignore template."""

REACT_TEMPLATE = {
    'name': 'React',
    'content': '''# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production builds
/build
/dist

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Debug logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
*.tsbuildinfo

# Next.js
.next/
out/

# Gatsby
.cache/
public

# Storybook build outputs
storybook-static

# Temporary folders
tmp/
temp/

# IDEs
.vscode/
.idea/

# OS generated files
.DS_Store
Thumbs.db

# ESLint cache
.eslintcache'''
}