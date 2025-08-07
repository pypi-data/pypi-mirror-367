"""
Command Line Interface for PowerPoint Template System

Provides CLI tools for generating presentations from JSON configurations
and creating sample presentations.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .enhanced_visual_generator import EnhancedVisualGenerator
from .enhanced_business_dsl import BusinessDSLBuilder, BusinessTheme
from .business_template_examples import (
    BusinessTemplateExamples,
)


def load_json_config(config_path: str) -> Dict[str, Any]:
    """Load JSON configuration file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        sys.exit(1)


def generate_from_json(config_path: str, output_dir: str = ".", presentation_name: Optional[str] = None) -> None:
    """Generate presentations from JSON configuration"""
    config = load_json_config(config_path)
    generator = EnhancedVisualGenerator()
    
    presentations_list = config.get('presentations', [])
    
    # Convert list to dict for easier handling
    presentations = {}
    for presentation in presentations_list:
        presentations[presentation.get('title', presentation.get('id', 'Unknown'))] = presentation
    
    if presentation_name:
        if presentation_name not in presentations:
            print(f"❌ Presentation '{presentation_name}' not found in configuration")
            print(f"Available presentations: {list(presentations.keys())}")
            sys.exit(1)
        presentations = {presentation_name: presentations[presentation_name]}
    
    print(f"🎯 Generating {len(presentations)} presentation(s) from configuration...")
    
    for name, presentation_config in presentations.items():
        print(f"📊 Generating presentation: {name}")
        
        # Create DSL presentation
        dsl = BusinessDSLBuilder()
        
        # Set metadata
        metadata = presentation_config.get('metadata', {})
        dsl.set_metadata(
            title=metadata.get('title', name),
            subtitle=metadata.get('subtitle', ''),
            author=metadata.get('author', ''),
            company=metadata.get('company', ''),
            date=metadata.get('date', '')
        )
        
        # Set theme
        theme_name = presentation_config.get('theme', 'corporate_blue')
        theme = BusinessTheme(theme_name)
        dsl.set_theme(theme)
        
        # Add slides
        slides = presentation_config.get('slides', [])
        for slide in slides:
            slide_type = slide.get('type', 'content')
            slide_id = slide.get('id', 'slide')
            slide_title = slide.get('title', '')
            content_type = slide.get('content_type', 'text')
            content_data = slide.get('content', {})
            
            if slide_type == 'title':
                dsl.add_title_slide()
            elif slide_type == 'section':
                dsl.add_section_divider(slide_id, slide_title)
            elif slide_type == 'content':
                dsl.add_content_slide(slide_id, slide_title, content_type, content_data)
            elif slide_type == 'thank_you':
                dsl.add_thank_you_slide()
        
        # Build and generate
        presentation = dsl.build()
        output_file = os.path.join(output_dir, f"{name.lower().replace(' ', '_')}_presentation.pptx")
        
        try:
            generator.create_presentation_from_dsl(presentation, output_file)
            print(f"✅ Created: {output_file}")
        except Exception as e:
            print(f"❌ Error generating {name}: {e}")
    
    print("🎉 Successfully generated presentations!")


def create_sample_presentations(output_dir: str = ".") -> None:
    """Create sample presentations using built-in templates"""
    print("🎯 Creating sample presentations...")
    
    samples = [
        ("Quarterly Business Review", BusinessTemplateExamples.create_quarterly_business_review),
        ("Sales Pitch", BusinessTemplateExamples.create_sales_pitch_presentation),
        ("Investor Pitch", BusinessTemplateExamples.create_investor_pitch_deck),
        ("Project Status Report", BusinessTemplateExamples.create_project_status_report),
    ]
    
    generator = EnhancedVisualGenerator()
    
    for name, create_func in samples:
        print(f"📊 Creating: {name}")
        try:
            presentation = create_func()
            output_file = os.path.join(output_dir, f"sample_{name.lower().replace(' ', '_')}.pptx")
            generator.create_presentation_from_dsl(presentation, output_file)
            print(f"✅ Created: {output_file}")
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
    
    print("🎉 Successfully created sample presentations!")


def list_available_presentations(config_path: str) -> None:
    """List available presentations in JSON configuration"""
    config = load_json_config(config_path)
    presentations_list = config.get('presentations', [])
    
    print(f"📋 Available presentations in {config_path}:")
    print()
    
    for presentation in presentations_list:
        name = presentation.get('title', presentation.get('id', 'Unknown'))
        presentation_config = presentation
        slides = presentation_config.get('slides', [])
        card_slides = sum(1 for slide in slides if slide.get('content_type') == 'card_grid')
        badges = sum(
            len(slide.get('content', {}).get('cards', []))
            for slide in slides 
            if slide.get('content_type') == 'card_grid'
        )
        
        print(f"📄 {name}")
        print(f"   Slides: {len(slides)}")
        if card_slides > 0:
            print(f"   Card Grids: {card_slides}")
            print(f"   Badges: {badges}")
        print()


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PowerPoint Template System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ppt-template generate config.json
  ppt-template generate config.json --presentation "Company Overview"
  ppt-template samples
  ppt-template list config.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate presentations from JSON')
    generate_parser.add_argument('config', help='JSON configuration file path')
    generate_parser.add_argument('--output', '-o', default='.', help='Output directory (default: current)')
    generate_parser.add_argument('--presentation', '-p', help='Generate specific presentation only')
    
    # Samples command
    samples_parser = subparsers.add_parser('samples', help='Create sample presentations')
    samples_parser.add_argument('--output', '-o', default='.', help='Output directory (default: current)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available presentations in JSON config')
    list_parser.add_argument('config', help='JSON configuration file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'generate':
        generate_from_json(args.config, args.output, args.presentation)
    elif args.command == 'samples':
        create_sample_presentations(args.output)
    elif args.command == 'list':
        list_available_presentations(args.config)


def generate() -> None:
    """Alternative entry point for ppt-generate command"""
    parser = argparse.ArgumentParser(description='Generate presentations from JSON configuration')
    parser.add_argument('config', help='JSON configuration file path')
    parser.add_argument('--output', '-o', default='.', help='Output directory (default: current)')
    parser.add_argument('--presentation', '-p', help='Generate specific presentation only')
    parser.add_argument('--list', '-l', action='store_true', help='List available presentations')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_presentations(args.config)
    else:
        generate_from_json(args.config, args.output, args.presentation)


if __name__ == '__main__':
    main() 