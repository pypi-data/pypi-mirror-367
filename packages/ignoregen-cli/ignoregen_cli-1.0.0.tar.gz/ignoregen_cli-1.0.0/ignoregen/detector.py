"""Project type detection functionality."""

import os
from pathlib import Path
from typing import List, Set


class ProjectDetector:
    """Detects project types based on files and directory structure."""
    
    def __init__(self):
        self.detection_rules = {
            'python': {
                'files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'conda.yml'],
                'extensions': ['.py'],
                'directories': ['venv', 'env', '.env', '__pycache__']
            },
            'nodejs': {
                'files': ['package.json', 'package-lock.json', 'yarn.lock', '.nvmrc'],
                'extensions': ['.js', '.ts'],
                'directories': ['node_modules', 'npm-debug.log*']
            },
            'react': {
                'files': ['package.json'],
                'extensions': ['.jsx', '.tsx'],
                'directories': ['build', 'dist'],
                'package_dependencies': ['react', 'react-dom', 'next', 'gatsby']
            },
            'django': {
                'files': ['manage.py', 'wsgi.py', 'asgi.py'],
                'directories': ['static', 'media', 'templates'],
                'python_imports': ['django']
            },
            'java': {
                'files': ['pom.xml', 'build.gradle', 'gradlew'],
                'extensions': ['.java', '.class'],
                'directories': ['target', 'build', '.gradle']
            },
            'cpp': {
                'files': ['CMakeLists.txt', 'Makefile'],
                'extensions': ['.cpp', '.c', '.h', '.hpp'],
                'directories': ['build', 'Debug', 'Release']
            }
        }
    
    def detect_project_types(self, project_path: str = ".") -> List[str]:
        """
        Detect project types in the given directory.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            List of detected project type names
        """
        path = Path(project_path).resolve()
        detected_types = set()
        
        # Get all files and directories in the project
        try:
            all_files = []
            all_dirs = []
            all_extensions = set()
            
            for item in path.rglob("*"):
                if item.is_file():
                    all_files.append(item.name)
                    if item.suffix:
                        all_extensions.add(item.suffix)
                elif item.is_dir():
                    all_dirs.append(item.name)
        except PermissionError:
            print(f"Warning: Permission denied accessing {path}")
            return []
        
        # Check each project type
        for project_type, rules in self.detection_rules.items():
            score = 0
            
            # Check for specific files
            if 'files' in rules:
                for file_name in rules['files']:
                    if file_name in all_files:
                        score += 2
            
            # Check for file extensions
            if 'extensions' in rules:
                for ext in rules['extensions']:
                    if ext in all_extensions:
                        score += 1
            
            # Check for directories
            if 'directories' in rules:
                for dir_name in rules['directories']:
                    if dir_name in all_dirs:
                        score += 1
            
            # Special checks for specific project types
            if project_type == 'react' and 'package.json' in all_files:
                package_json_path = path / 'package.json'
                if self._check_package_json_dependencies(
                    package_json_path, rules.get('package_dependencies', [])
                ):
                    score += 3
            
            if project_type == 'django' and score > 0:
                # Additional check for Django-specific patterns
                if self._check_django_patterns(path):
                    score += 2
            
            # If score is high enough, consider it detected
            if score >= 2:
                detected_types.add(project_type)
        
        return list(detected_types)
    
    def _check_package_json_dependencies(self, package_json_path: Path, dependencies: List[str]) -> bool:
        """Check if package.json contains specific dependencies."""
        try:
            import json
            content = json.loads(package_json_path.read_text())
            all_deps = {}
            all_deps.update(content.get('dependencies', {}))
            all_deps.update(content.get('devDependencies', {}))
            
            return any(dep in all_deps for dep in dependencies)
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def _check_django_patterns(self, path: Path) -> bool:
        """Check for Django-specific patterns in Python files."""
        try:
            for py_file in path.rglob("*.py"):
                if py_file.is_file():
                    try:
                        content = py_file.read_text()
                        if 'from django' in content or 'import django' in content:
                            return True
                    except (UnicodeDecodeError, PermissionError):
                        continue
        except Exception:
            pass
        return False