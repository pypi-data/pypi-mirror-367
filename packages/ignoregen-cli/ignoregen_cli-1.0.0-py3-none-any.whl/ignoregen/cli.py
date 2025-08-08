"""Command line interface for IgnoreGen."""

import argparse
import sys
from pathlib import Path
from .core import IgnoreGen


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IgnoreGen - Smart .gitignore Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ignoregen python                    # Generate Python .gitignore
  ignoregen python nodejs            # Combine Python and Node.js templates
  ignoregen --auto-detect            # Auto-detect project type
  ignoregen --list                   # List available templates
  ignoregen --output myproject       # Save to specific directory
  ignoregen python --dry-run         # Preview without saving
        """
    )
    
    parser.add_argument(
        'templates', 
        nargs='*',
        help='Template names to use (e.g., python, nodejs, react)'
    )
    
    parser.add_argument(
        '-a', '--auto-detect',
        action='store_true',
        help='Auto-detect project type based on files'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available templates'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Show output without saving file'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Don\'t backup existing .gitignore'
    )
    
    parser.add_argument(
        '--no-merge',
        action='store_true',
        help='Don\'t merge with existing .gitignore'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = IgnoreGen()
    
    # List templates if requested
    if args.list:
        print("Available templates:")
        for template_name in sorted(generator.get_available_templates()):
            template = generator.templates[template_name]
            print(f"  {template_name:12} - {template['name']}")
        return 0
    
    # Check if templates or auto-detect specified
    if not args.templates and not args.auto_detect:
        print("Error: Specify template names or use --auto-detect")
        parser.print_help()
        return 1
    
    # Validate output directory
    output_path = Path(args.output).resolve()
    if not output_path.exists():
        print(f"Error: Output directory '{output_path}' does not exist")
        return 1
    
    # Validate templates
    if args.templates:
        invalid_templates = []
        available = generator.get_available_templates()
        for template in args.templates:
            if template.lower() not in available:
                invalid_templates.append(template)
        
        if invalid_templates:
            print(f"Error: Unknown templates: {', '.join(invalid_templates)}")
            print(f"Available templates: {', '.join(sorted(available))}")
            return 1
    
    try:
        # Generate content
        if args.verbose:
            print(f"Generating .gitignore for: {output_path}")
            if args.templates:
                print(f"Using templates: {', '.join(args.templates)}")
            if args.auto_detect:
                print("Auto-detecting project types...")
        
        content = generator.generate(
            template_names=args.templates,
            auto_detect=args.auto_detect,
            project_path=str(output_path),
            merge_existing=not args.no_merge
        )
        
        if args.dry_run:
            print("Generated .gitignore content:")
            print("-" * 40)
            print(content)
            print("-" * 40)
        else:
            generator.save_gitignore(
                content=content,
                project_path=str(output_path),
                backup_existing=not args.no_backup
            )
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())