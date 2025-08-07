#!/usr/bin/env python3
"""
Merge Style and Content Templates

This script combines a style template (presentation structure and styling)
with a content template (actual text, images, data) to create a complete
presentation configuration that can be used by the PowerPoint Template System.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)


def merge_style_and_content(style_data: Dict[str, Any], content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge style template with content template to create a complete presentation configuration.
    
    Args:
        style_data: Style template containing presentation structure and styling
        content_data: Content template containing actual text, images, and data
    
    Returns:
        Complete presentation configuration ready for PowerPoint generation
    """
    
    # Extract the main objects
    style = style_data.get('presentation_style', {})
    content = content_data.get('presentation_content', {})
    
    # Create the merged presentation
    merged_presentation = {
        "presentations": [{
            "id": content.get('id', 'merged_presentation'),
            "title": content.get('title', 'Merged Presentation'),
            "subtitle": content.get('subtitle', ''),
            "author": content.get('author', ''),
            "company": content.get('company', ''),
            "date": content.get('date', '2024'),
            "theme": style.get('theme', 'corporate_blue'),
            "slides": []
        }]
    }
    
    # Get the slide structure from style
    slide_structure = style.get('slide_structure', [])
    content_slides = content.get('slides', [])
    
    # Create a mapping of slide IDs for easy lookup
    content_slide_map = {slide['id']: slide for slide in content_slides}
    
    # Merge each slide
    for style_slide in slide_structure:
        slide_id = style_slide['id']
        slide_type = style_slide['type']
        
        # Find corresponding content slide
        content_slide = content_slide_map.get(slide_id)
        
        if content_slide:
            # Merge style and content for this slide
            merged_slide = {
                "id": slide_id,
                "type": slide_type,
                "content": content_slide['content']
            }
            
            # Add styling information if available
            if 'style' in style_slide:
                merged_slide['style'] = style_slide['style']
            
            merged_presentation['presentations'][0]['slides'].append(merged_slide)
        else:
            print(f"⚠️  Warning: No content found for slide '{slide_id}'")
    
    return merged_presentation


def validate_merged_config(config: Dict[str, Any]) -> bool:
    """
    Validate the merged configuration to ensure it's complete and correct.
    
    Args:
        config: The merged configuration to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        presentations = config.get('presentations', [])
        if not presentations:
            print("❌ Error: No presentations found in merged config")
            return False
        
        presentation = presentations[0]
        required_fields = ['id', 'title', 'slides']
        
        for field in required_fields:
            if field not in presentation:
                print(f"❌ Error: Missing required field '{field}' in presentation")
                return False
        
        slides = presentation.get('slides', [])
        if not slides:
            print("❌ Error: No slides found in presentation")
            return False
        
        for i, slide in enumerate(slides):
            if 'id' not in slide or 'type' not in slide or 'content' not in slide:
                print(f"❌ Error: Slide {i+1} missing required fields (id, type, content)")
                return False
        
        print("✅ Merged configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating merged config: {e}")
        return False


def main():
    """Main function to merge style and content templates."""
    
    if len(sys.argv) != 4:
        print("Usage: python merge_style_content.py <style_file> <content_file> <output_file>")
        print("\nExample:")
        print("  python merge_style_content.py ai_agent_style_template.json ai_agent_content_template.json merged_presentation.json")
        sys.exit(1)
    
    style_file = sys.argv[1]
    content_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print("🔄 Loading style template...")
    style_data = load_json_file(style_file)
    
    print("🔄 Loading content template...")
    content_data = load_json_file(content_file)
    
    print("🔄 Merging style and content...")
    merged_config = merge_style_and_content(style_data, content_data)
    
    print("🔄 Validating merged configuration...")
    if not validate_merged_config(merged_config):
        sys.exit(1)
    
    # Save the merged configuration
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Merged configuration saved to '{output_file}'")
        
        # Print summary
        presentation = merged_config['presentations'][0]
        slides = presentation['slides']
        
        print(f"\n📊 Summary:")
        print(f"   Presentation: {presentation['title']}")
        print(f"   Author: {presentation['author']}")
        print(f"   Company: {presentation['company']}")
        print(f"   Theme: {presentation['theme']}")
        print(f"   Slides: {len(slides)}")
        
        # Count different slide types
        slide_types = {}
        for slide in slides:
            slide_type = slide['type']
            slide_types[slide_type] = slide_types.get(slide_type, 0) + 1
        
        print(f"   Slide Types:")
        for slide_type, count in slide_types.items():
            print(f"     - {slide_type}: {count}")
        
        print(f"\n🚀 You can now generate the presentation with:")
        print(f"   ppt-template generate {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving merged configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 