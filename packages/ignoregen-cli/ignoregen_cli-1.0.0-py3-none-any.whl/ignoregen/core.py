"""Core functionality for IgnoreGen."""

import os
from pathlib import Path
from typing import List, Optional, Set
from .templates import TEMPLATES
from .detector import ProjectDetector


class IgnoreGen:
    """Main class for generating .gitignore files."""
    
    def __init__(self):
        self.detector = ProjectDetector()
        self.templates = TEMPLATES
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def generate(self, 
                 template_names: Optional[List[str]] = None,
                 auto_detect: bool = False,
                 project_path: str = ".",
                 merge_existing: bool = True) -> str:
        """
        Generate .gitignore content.
        
        Args:
            template_names: List of template names to use
            auto_detect: Whether to auto-detect project type
            project_path: Path to project directory
            merge_existing: Whether to merge with existing .gitignore
            
        Returns:
            Generated .gitignore content as string
        """
        content_parts = []
        used_templates = set()
        
        # Auto-detect if requested
        if auto_detect:
            detected = self.detector.detect_project_types(project_path)
            if detected:
                template_names = template_names or []
                template_names.extend(detected)
        
        # Use provided templates
        if template_names:
            for template_name in template_names:
                template_name = template_name.lower()
                if template_name in self.templates and template_name not in used_templates:
                    template = self.templates[template_name]
                    content_parts.append(f"# {template['name']} .gitignore")
                    content_parts.append(template['content'])
                    content_parts.append("")  # Empty line
                    used_templates.add(template_name)
        
        # If no templates specified and no auto-detection, use base template
        if not content_parts:
            base_template = self.templates['base']
            content_parts.append(f"# {base_template['name']} .gitignore")
            content_parts.append(base_template['content'])
        
        # Merge with existing .gitignore if requested
        existing_content = ""
        if merge_existing:
            existing_path = Path(project_path) / ".gitignore"
            if existing_path.exists():
                existing_content = existing_path.read_text().strip()
                if existing_content:
                    content_parts.insert(0, "# Existing .gitignore content")
                    content_parts.insert(1, existing_content)
                    content_parts.insert(2, "")
        
        return "\n".join(content_parts).strip()
    
    def save_gitignore(self, 
                       content: str, 
                       project_path: str = ".",
                       backup_existing: bool = True) -> None:
        """
        Save .gitignore content to file.
        
        Args:
            content: .gitignore content to save
            project_path: Path to project directory
            backup_existing: Whether to backup existing .gitignore
        """
        gitignore_path = Path(project_path) / ".gitignore"
        
        # Backup existing file if requested
        if backup_existing and gitignore_path.exists():
            backup_path = gitignore_path.with_suffix(".gitignore.backup")
            gitignore_path.replace(backup_path)
            print(f"Backed up existing .gitignore to {backup_path}")
        
        # Write new content
        gitignore_path.write_text(content + "\n")
        print(f"Generated .gitignore saved to {gitignore_path}")


def generate_gitignore(template_names: Optional[List[str]] = None,
                      auto_detect: bool = False,
                      project_path: str = ".") -> str:
    """
    Convenience function to generate .gitignore content.
    
    Args:
        template_names: List of template names to use
        auto_detect: Whether to auto-detect project type
        project_path: Path to project directory
        
    Returns:
        Generated .gitignore content as string
    """
    generator = IgnoreGen()
    return generator.generate(template_names, auto_detect, project_path)