"""
Generate Enhanced PowerPoint Presentations from JSON Configuration

This script reads a JSON configuration file and generates professional
PowerPoint presentations with images and enhanced styling.
"""

import json
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.powerpoint_templates import (
    BusinessDSLBuilder, 
    BusinessTheme, 
    EnhancedVisualGenerator
)


class JSONPresentationGenerator:
    """Generate presentations from JSON configuration"""
    
    def __init__(self, config_file="presentation_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.generator = EnhancedVisualGenerator()
    
    def _load_config(self):
        """Load JSON configuration file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file '{self.config_file}' not found!")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            return None
    
    def _get_theme_enum(self, theme_name):
        """Convert theme name to BusinessTheme enum"""
        theme_mapping = {
            'corporate_blue': BusinessTheme.CORPORATE_BLUE,
            'startup_vibrant': BusinessTheme.STARTUP_VIBRANT,
            'modern_minimal': BusinessTheme.MODERN_MINIMAL,
            'executive_dark': BusinessTheme.EXECUTIVE_DARK,
            'consulting_clean': BusinessTheme.CONSULTING_CLEAN,
            'financial_professional': BusinessTheme.FINANCIAL_PROFESSIONAL
        }
        return theme_mapping.get(theme_name, BusinessTheme.CORPORATE_BLUE)
    
    def _build_presentation_from_config(self, presentation_config):
        """Build presentation DSL from JSON configuration"""
        builder = BusinessDSLBuilder()
        
        # Set metadata
        builder.set_metadata(
            title=presentation_config.get('title', 'Presentation'),
            subtitle=presentation_config.get('subtitle', ''),
            author=presentation_config.get('author', ''),
            company=presentation_config.get('company', ''),
            date=presentation_config.get('date', '')
        )
        
        # Set theme
        theme_name = presentation_config.get('theme', 'corporate_blue')
        theme_enum = self._get_theme_enum(theme_name)
        builder.set_theme(theme_enum)
        
        # Add slides
        slides = presentation_config.get('slides', [])
        for slide_config in slides:
            slide_id = slide_config.get('id', 'slide')
            slide_type = slide_config.get('type', 'content')
            content = slide_config.get('content', {})
            
            if slide_type == 'title':
                builder.add_title_slide(slide_id)
            
            elif slide_type == 'agenda':
                items = content.get('items', [])
                builder.add_agenda_slide(slide_id, items)
            
            elif slide_type == 'image_with_text':
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'image_with_text',
                    {
                        'image_path': content.get('image_path', ''),
                        'image_position': content.get('image_position', 'left'),
                        'text_content': content.get('text_content', []),
                        'image_width': content.get('image_width', 3.0),
                        'image_height': content.get('image_height', 2.5)
                    }
                )
            
            elif slide_type == 'image_focus':
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'image_focus',
                    {
                        'image_path': content.get('image_path', ''),
                        'image_width': content.get('image_width', 6.0),
                        'image_height': content.get('image_height', 4.0),
                        'caption': content.get('caption', '')
                    }
                )
            
            elif slide_type == 'image_grid':
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'image_grid',
                    {
                        'images': content.get('images', []),
                        'layout': content.get('layout', '2x2')
                    }
                )
            
            elif slide_type == 'icon_grid':
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'icon_grid',
                    {
                        'icons': content.get('icons', []),
                        'layout': content.get('layout', '2x2')
                    }
                )
            
            elif slide_type == 'mixed_content':
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'mixed_content',
                    {
                        'chart_data': content.get('chart_data', {}),
                        'image_path': content.get('image_path', ''),
                        'image_position': content.get('image_position', 'bottom'),
                        'image_width': content.get('image_width', 4.0),
                        'image_height': content.get('image_height', 2.0)
                    }
                )
            elif slide_type == 'card_grid':
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'card_grid',
                    {
                        'cards': content.get('cards', []),
                        'layout': content.get('layout', 'horizontal'),
                        'background_color': content.get('background_color', '#1f4e79'),
                        'card_spacing': content.get('card_spacing', 0.3)
                    }
                )
            
            elif slide_type == 'thank_you':
                contact_info = content.get('contact_info', {})
                builder.add_thank_you_slide(slide_id, contact_info)
            
            else:
                # Default content slide
                builder.add_content_slide(
                    slide_id,
                    content.get('title', ''),
                    'bullet_list',
                    {'items': content.get('text_content', [])}
                )
        
        return builder.build()
    
    def generate_presentation(self, presentation_id):
        """Generate a specific presentation by ID"""
        if not self.config:
            return None
        
        presentations = self.config.get('presentations', [])
        presentation_config = None
        
        for pres in presentations:
            if pres.get('id') == presentation_id:
                presentation_config = pres
                break
        
        if not presentation_config:
            print(f"❌ Presentation '{presentation_id}' not found in configuration!")
            return None
        
        print(f"📊 Generating presentation: {presentation_config['title']}")
        
        # Count card grids and badges for reporting
        card_count = 0
        badge_count = 0
        slides = presentation_config.get('slides', [])
        for slide in slides:
            if slide.get('type') == 'card_grid':
                card_count += 1
                cards = slide.get('content', {}).get('cards', [])
                for card in cards:
                    if card.get('badge'):
                        badge_count += 1
        
        if card_count > 0:
            print(f"   📋 Found {card_count} card grid slide(s) with {badge_count} badge(s)")
        
        # Build presentation from config
        presentation_dsl = self._build_presentation_from_config(presentation_config)
        
        # Generate PowerPoint file
        output_filename = f"{presentation_id}_presentation.pptx"
        output_file = self.generator.create_presentation_from_dsl(presentation_dsl, output_filename)
        
        print(f"✅ Created: {output_file}")
        return output_file
    
    def generate_all_presentations(self):
        """Generate all presentations from configuration"""
        if not self.config:
            return []
        
        presentations = self.config.get('presentations', [])
        generated_files = []
        
        print(f"🎯 Generating {len(presentations)} presentations from configuration...\n")
        
        for presentation_config in presentations:
            presentation_id = presentation_config.get('id', 'unknown')
            output_file = self.generate_presentation(presentation_id)
            if output_file:
                generated_files.append(output_file)
        
        return generated_files
    
    def list_available_presentations(self):
        """List all available presentations in configuration"""
        if not self.config:
            return
        
        presentations = self.config.get('presentations', [])
        print(f"📋 Available presentations in '{self.config_file}':")
        
        for i, pres in enumerate(presentations, 1):
            title = pres.get('title', 'Untitled')
            subtitle = pres.get('subtitle', '')
            theme = pres.get('theme', 'corporate_blue')
            slides_count = len(pres.get('slides', []))
            
            # Count card grids and badges
            card_count = 0
            badge_count = 0
            slides = pres.get('slides', [])
            for slide in slides:
                if slide.get('type') == 'card_grid':
                    card_count += 1
                    cards = slide.get('content', {}).get('cards', [])
                    for card in cards:
                        if card.get('badge'):
                            badge_count += 1
            
            print(f"  {i}. {pres.get('id', 'unknown')} - {title}")
            if subtitle:
                print(f"     Subtitle: {subtitle}")
            print(f"     Theme: {theme}")
            print(f"     Slides: {slides_count}")
            if card_count > 0:
                print(f"     🎴 Card Grids: {card_count} slide(s)")
                print(f"     🏷️  Badges: {badge_count} total")
            print()


def main():
    """Main function to run the JSON presentation generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate PowerPoint presentations from JSON configuration')
    parser.add_argument('--config', default='presentation_config.json', 
                       help='JSON configuration file path')
    parser.add_argument('--presentation', '-p', 
                       help='Generate specific presentation by ID')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available presentations')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Generate all presentations')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = JSONPresentationGenerator(args.config)
    
    if args.list:
        generator.list_available_presentations()
        return
    
    if args.presentation:
        # Generate specific presentation
        output_file = generator.generate_presentation(args.presentation)
        if output_file:
            print(f"\n🎉 Successfully generated: {output_file}")
    elif args.all:
        # Generate all presentations
        generated_files = generator.generate_all_presentations()
        print(f"\n🎉 Successfully generated {len(generated_files)} presentations!")
        print("\nGenerated files:")
        for file in generated_files:
            if os.path.exists(file):
                file_size = os.path.getsize(file) / 1024
                print(f"  📄 {file} ({file_size:.1f} KB)")
    else:
        # Default: generate all presentations
        print("=== JSON-Powered PowerPoint Generator ===\n")
        generator.list_available_presentations()
        print("Generating all presentations...\n")
        generated_files = generator.generate_all_presentations()
        print(f"\n🎉 Successfully generated {len(generated_files)} presentations!")
        print("\nGenerated files:")
        for file in generated_files:
            if os.path.exists(file):
                file_size = os.path.getsize(file) / 1024
                print(f"  📄 {file} ({file_size:.1f} KB)")


if __name__ == "__main__":
    main() 