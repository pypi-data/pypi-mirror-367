"""Template definitions for different project types."""

from .python import PYTHON_TEMPLATE
from .nodejs import NODEJS_TEMPLATE
from .react import REACT_TEMPLATE
from .django import DJANGO_TEMPLATE
from .java import JAVA_TEMPLATE
from .cpp import CPP_TEMPLATE
from .base import BASE_TEMPLATE

TEMPLATES = {
    'base': BASE_TEMPLATE,
    'python': PYTHON_TEMPLATE,
    'nodejs': NODEJS_TEMPLATE,
    'node': NODEJS_TEMPLATE,  # Alias
    'react': REACT_TEMPLATE,
    'django': DJANGO_TEMPLATE,
    'java': JAVA_TEMPLATE,
    'cpp': CPP_TEMPLATE,
    'c++': CPP_TEMPLATE,  # Alias
}