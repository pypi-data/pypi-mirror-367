"""Tests for core functionality."""

import unittest
import tempfile
from pathlib import Path
from ignoregen.core import IgnoreGen, generate_gitignore


class TestIgnoreGen(unittest.TestCase):
    
    def setUp(self):
        self.generator = IgnoreGen()
    
    def test_get_available_templates(self):
        templates = self.generator.get_available_templates()
        self.assertIn('python', templates)
        self.assertIn('nodejs', templates)
        self.assertIn('react', templates)
    
    def test_generate_python_template(self):
        content = self.generator.generate(['python'])
        self.assertIn('__pycache__/', content)
        self.assertIn('*.py[cod]', content)
    
    def test_generate_multiple_templates(self):
        content = self.generator.generate(['python', 'nodejs'])
        self.assertIn('__pycache__/', content)  # Python
        self.assertIn('node_modules/', content)  # Node.js
    
    def test_generate_no_templates(self):
        content = self.generator.generate()
        self.assertIn('Base', content)
    
    def test_convenience_function(self):
        content = generate_gitignore(['python'])
        self.assertIn('__pycache__/', content)


if __name__ == '__main__':
    unittest.main()