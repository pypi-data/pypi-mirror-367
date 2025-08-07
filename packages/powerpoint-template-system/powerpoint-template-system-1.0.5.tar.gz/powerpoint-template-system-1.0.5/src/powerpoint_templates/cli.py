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
        
        # Set metadata - handle both metadata object and direct fields
        metadata = presentation_config.get('metadata', {})
        dsl.set_metadata(
            title=metadata.get('title', presentation_config.get('title', name)),
            subtitle=metadata.get('subtitle', presentation_config.get('subtitle', '')),
            author=metadata.get('author', presentation_config.get('author', '')),
            company=metadata.get('company', presentation_config.get('company', '')),
            date=metadata.get('date', presentation_config.get('date', ''))
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
            elif slide_type == 'card_grid':
                # Handle card grid slides
                title = content_data.get('title', '')
                cards = content_data.get('cards', [])
                dsl.add_content_slide(slide_id, title, 'card_grid', content_data)
            elif slide_type == 'image_with_text':
                # Handle image with text slides
                title = content_data.get('title', '')
                dsl.add_content_slide(slide_id, title, 'image_with_text', content_data)
            elif slide_type == 'image_focus':
                # Handle image focus slides
                title = content_data.get('title', '')
                dsl.add_content_slide(slide_id, title, 'image_focus', content_data)
            elif slide_type == 'image_grid':
                # Handle image grid slides
                title = content_data.get('title', '')
                dsl.add_content_slide(slide_id, title, 'image_grid', content_data)
            elif slide_type == 'thank_you':
                dsl.add_thank_you_slide()
            else:
                # Default to content slide
                dsl.add_content_slide(slide_id, slide_title, content_type, content_data)
        
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


def show_schema_info(xsd_path: str = None) -> None:
    """Show information about the XSD schema and DSL capabilities"""
    if xsd_path is None:
        xsd_path = "pptx_dsl_schema_enhanced.xsd"
    
    print("📋 PowerPoint Template System - XSD Schema Information")
    print("=" * 60)
    print()
    
    print("🎯 **DSL (Domain Specific Language) Schema**")
    print(f"📄 Schema File: {xsd_path}")
    print("🌐 Namespace: http://pptx-dsl.com/schema")
    print()
    
    print("📊 **Key Schema Components:**")
    print()
    print("🏗️  **Presentation Structure**")
    print("   • PresentationType: Root element with metadata, theme, and slides")
    print("   • MetadataType: Title, subtitle, author, company, date")
    print("   • ThemeType: Colors, fonts, and card styles")
    print()
    
    print("🎨 **Enhanced Styling Features**")
    print("   • CardStylesType: Modern, classic, creative card styles")
    print("   • GradientBackgroundType: Linear and radial gradients")
    print("   • CardShadowType: Configurable shadows with offset and blur")
    print("   • CardTypographyType: Custom fonts, sizes, colors, spacing")
    print()
    
    print("🃏 **Card System**")
    print("   • CardType: Complete card structure with image, category, title, description")
    print("   • CardBadgeType: Configurable badges with positions and sizes")
    print("   • CardStylingType: Background, border, shadow, and corner rounding")
    print("   • CardGridLayoutType: Responsive grid layouts for cards")
    print()
    
    print("📱 **Responsive Layouts**")
    print("   • ResponsiveConfigType: Auto-adjustment and breakpoints")
    print("   • LayoutBreakpointType: Device-specific layouts")
    print("   • EnhancedLayoutType: Auto, grid, flex, absolute positioning")
    print()
    
    print("🎯 **Content Types**")
    print("   • EnhancedTextContentType: Rich text with effects and styling")
    print("   • ImageContentType: Images with fit options and rounding")
    print("   • ChartContentType: Various chart types with data series")
    print("   • TableContentType: Structured tables with cell spanning")
    print()
    
    print("🎨 **Theme System**")
    print("   • ThemeNameType: corporate_blue, startup_vibrant, modern_minimal")
    print("   • ColorsType: Primary, secondary, accent, background colors")
    print("   • FontsType: Heading, body, category, title, description fonts")
    print()
    
    print("🔧 **Advanced Features**")
    print("   • Text effects: shadows, outlines, transforms")
    print("   • Border styles: solid, dashed, dotted")
    print("   • Gradient types: linear, radial with directions")
    print("   • Badge positions: top-right, top-left, bottom-right, bottom-left")
    print("   • Overflow handling: clip, ellipsis, wrap, scale, scroll")
    print()
    
    print("📖 **Usage Examples:**")
    print("   • JSON Configuration: examples/presentation_config.json")
    print("   • Card Examples: examples/card_presentation_config.json")
    print("   • Demo Scripts: examples/badge_demo.py, examples/modern_styling_demo.py")
    print()
    
    print("🔗 **Schema Validation:**")
    print("   • Use the XSD schema to validate your DSL definitions")
    print("   • Ensures proper structure and data types")
    print("   • Supports modern presentation features and styling")
    print()


def show_ai_agent_guide(template_type: str = None) -> None:
    """Show comprehensive AI Agent guide for creating templates"""
    print("🤖 **AI Agent Guide - PowerPoint Template Creation**")
    print("=" * 70)
    print()
    
    print("🎯 **Overview for AI Agents**")
    print("This guide helps AI agents create professional PowerPoint presentations")
    print("using the PowerPoint Template System's XSD schema and JSON configuration.")
    print("You can use either single JSON files or separate style and content templates.")
    print()
    
    print("📋 **Step-by-Step Template Creation Process**")
    print()
    
    print("🔍 **Step 1: Understand the XSD Schema Structure**")
    print("   • Review pptx_dsl_schema_enhanced.xsd for available elements")
    print("   • Key root elements: <presentation>, <metadata>, <theme>, <slide>")
    print("   • Content types: <text>, <image>, <chart>, <table>, <card>")
    print("   • Styling options: gradients, shadows, borders, typography")
    print()
    
    print("🏗️  **Step 2: Define Presentation Structure**")
    print("   • Start with <presentation> as root element")
    print("   • Add <metadata> with title, subtitle, author, company, date")
    print("   • Choose <theme> from available options or create custom")
    print("   • Plan <slide> sequence for logical flow")
    print()
    
    print("🎨 **Step 3: Design Slide Layouts**")
    print("   • Use <layout> elements for positioning")
    print("   • Available layouts: auto, grid, flex, absolute, card-grid")
    print("   • Configure responsive behavior with breakpoints")
    print("   • Set spacing, padding, and alignment")
    print()
    
    print("📝 **Step 4: Add Content Elements**")
    print("   • <text>: Rich text with styling and effects")
    print("   • <image>: Images with fit options and rounding")
    print("   • <chart>: Various chart types with data series")
    print("   • <table>: Structured tables with cell spanning")
    print("   • <card>: Modern card layouts with badges")
    print()
    
    print("🎯 **Step 5: Apply Modern Styling**")
    print("   • Card backgrounds: solid colors or gradients")
    print("   • Shadows: configurable offset, blur, and color")
    print("   • Borders: solid, dashed, dotted styles")
    print("   • Typography: custom fonts, sizes, colors, spacing")
    print("   • Badges: positions, sizes, colors, text")
    print()
    
    print("🔧 **Step 6: Create JSON Configuration**")
    print("   • Option A: Single JSON file with style and content")
    print("   • Option B: Separate style and content templates")
    print("   • Use examples/presentation_config.json as reference")
    print("   • Use merge_style_content.py to combine templates")
    print("   • Ensure proper nesting and data types")
    print("   • Validate against schema requirements")
    print()
    
    print("🚀 **Step 7: Generate Presentation**")
    print("   • Use CLI: ppt-template generate config.json")
    print("   • Specify output directory and presentation name")
    print("   • Verify generated PowerPoint file")
    print("   • Test with different themes and content")
    print()
    
    print("📊 **Key Schema Elements for AI Agents**")
    print()
    
    print("🎯 **Presentation Structure**")
    print("   <presentation>")
    print("     <metadata>")
    print("       <title>Your Presentation Title</title>")
    print("       <subtitle>Subtitle or description</subtitle>")
    print("       <author>Author Name</author>")
    print("       <company>Company Name</company>")
    print("       <date>2024</date>")
    print("     </metadata>")
    print("     <theme name='corporate_blue'/>")
    print("     <slide>...</slide>")
    print("   </presentation>")
    print()
    
    print("🃏 **Card System Example**")
    print("   <slide template='card-grid'>")
    print("     <layout type='card-grid' columns='3'>")
    print("       <card>")
    print("         <image path='image.png' rounded='true'/>")
    print("         <category>CATEGORY</category>")
    print("         <title>Card Title</title>")
    print("         <description>Card description text</description>")
    print("         <badge>")
    print("           <text>NEW</text>")
    print("           <color>#28a745</color>")
    print("           <position>top-right</position>")
    print("         </badge>")
    print("         <styling>")
    print("           <background>")
    print("             <gradient>")
    print("               <color>#ffffff</color>")
    print("               <color>#f8f9fa</color>")
    print("             </gradient>")
    print("           </background>")
    print("           <shadow enabled='true'/>")
    print("           <roundedCorners>true</roundedCorners>")
    print("         </styling>")
    print("       </card>")
    print("     </layout>")
    print("   </slide>")
    print()
    
    print("📝 **JSON Configuration Options**")
    print()
    print("🎨 **Option A: Single JSON (Style + Content)**")
    print("   {")
    print("     'presentations': [")
    print("       {")
    print("         'id': 'ai_generated',")
    print("         'title': 'AI Generated Presentation',")
    print("         'theme': 'corporate_blue',")
    print("         'slides': [")
    print("           {")
    print("             'id': 'title',")
    print("             'type': 'title',")
    print("             'content': {")
    print("               'title': 'AI Generated Presentation',")
    print("               'subtitle': 'Modern and Professional'")
    print("             }")
    print("           }")
    print("         ]")
    print("       }")
    print("     ]")
    print("   }")
    print()
    print("🎨 **Option B: Separate Style and Content Templates**")
    print("   Style Template (ai_agent_style_template.json):")
    print("   {")
    print("     'presentation_style': {")
    print("       'id': 'business_presentation_style',")
    print("       'theme': 'corporate_blue',")
    print("       'slide_structure': [")
    print("         {")
    print("           'id': 'title_slide',")
    print("           'type': 'title',")
    print("           'style': { ... },")
    print("           'content_placeholders': {")
    print("             'title': 'string',")
    print("             'subtitle': 'string'")
    print("           }")
    print("         }")
    print("       ]")
    print("     }")
    print("   }")
    print()
    print("   Content Template (ai_agent_content_template.json):")
    print("   {")
    print("     'presentation_content': {")
    print("       'id': 'tech_company_presentation',")
    print("       'title': 'TechCorp Innovation Overview',")
    print("       'slides': [")
    print("         {")
    print("           'id': 'title_slide',")
    print("           'content': {")
    print("             'title': 'TechCorp Innovation Overview',")
    print("             'subtitle': 'Leading the Future of Technology'")
    print("           }")
    print("         }")
    print("       ]")
    print("     }")
    print("   }")
    print()
    print("   Merge Command:")
    print("   python merge_style_content.py style.json content.json output.json")
    print()
    
    print("🎯 **AI Agent Best Practices**")
    print()
    print("✅ **Content Organization**")
    print("   • Start with clear title and agenda slides")
    print("   • Use consistent styling across slides")
    print("   • Balance text, images, and visual elements")
    print("   • Include call-to-action slides")
    print()
    
    print("✅ **Visual Design**")
    print("   • Choose appropriate themes for content type")
    print("   • Use cards for feature highlights")
    print("   • Apply badges for status indicators")
    print("   • Implement gradients and shadows for depth")
    print()
    
    print("✅ **Template Strategy**")
    print("   • Use style templates for consistent branding")
    print("   • Create content templates for different topics")
    print("   • Combine style and content for flexibility")
    print("   • Reuse templates across multiple presentations")
    print()
    
    print("✅ **Technical Implementation**")
    print("   • Validate JSON against XSD schema")
    print("   • Test with different themes")
    print("   • Ensure responsive layouts")
    print("   • Optimize for readability")
    print()
    
    print("🔧 **CLI Commands for AI Agents**")
    print()
    print("   # Generate from AI template")
    print("   ppt-template generate examples/ai_agent_template.json")
    print()
    print("   # Generate from merged style/content")
    print("   python examples/merge_style_content.py style.json content.json output.json")
    print("   ppt-template generate output.json")
    print()
    print("   # Generate custom presentation")
    print("   ppt-template generate ai_presentation.json")
    print()
    print("   # List available presentations")
    print("   ppt-template list ai_presentation.json")
    print()
    print("   # View schema information")
    print("   ppt-template schema")
    print()
    print("   # Create sample presentations")
    print("   ppt-template samples")
    print()
    
    print("📖 **Reference Files**")
    print("   • XSD Schema: pptx_dsl_schema_enhanced.xsd")
    print("   • JSON Examples: examples/presentation_config.json")
    print("   • AI Template: examples/ai_agent_template.json")
    print("   • Style Template: examples/ai_agent_style_template.json")
    print("   • Content Template: examples/ai_agent_content_template.json")
    print("   • Merge Script: examples/merge_style_content.py")
    print("   • Card Examples: examples/card_presentation_config.json")
    print("   • Demo Scripts: examples/badge_demo.py")
    print()
    
    if template_type:
        print(f"🎯 **Custom Template for: {template_type}**")
        print("   (Custom template generation would be implemented here)")
        print()


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
        description="PowerPoint Template System CLI - Create professional presentations with modern styling, cards, and badges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ppt-template generate config.json
  ppt-template generate config.json --presentation "Company Overview"
  ppt-template samples
  ppt-template list config.json
  ppt-template schema
  ppt-template ai-guide

Documentation:
  JSON Configuration: Use JSON files to define presentations with slides, content, and styling
  XSD Schema: pptx_dsl_schema_enhanced.xsd provides XML schema validation for DSL definitions
  AI Agent Guide: Use ppt-template ai-guide for comprehensive AI agent instructions
  Features: Modern cards, badges, gradients, shadows, and responsive layouts
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
    
    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Show information about XSD schema and DSL')
    schema_parser.add_argument('--xsd', help='Path to XSD schema file (default: pptx_dsl_schema_enhanced.xsd)')
    
    # AI Agent guide command
    ai_guide_parser = subparsers.add_parser('ai-guide', help='Show AI Agent guide for creating templates')
    ai_guide_parser.add_argument('--template', help='Generate example template for specific use case')
    
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
    elif args.command == 'schema':
        show_schema_info(args.xsd)
    elif args.command == 'ai-guide':
        show_ai_agent_guide(args.template)


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