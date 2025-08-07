"""
Card System Demo

This script demonstrates the article card system for PowerPoint presentations.
"""

import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.powerpoint_templates import (
    BusinessDSLBuilder, 
    BusinessTheme, 
    EnhancedVisualGenerator
)


def create_card_demo():
    """Create a demo presentation with article cards"""
    print("Creating card demo presentation...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Article Cards Demo",
            subtitle="Modern Card-Based Layout",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_content_slide(
            "travel_cards",
            "Travel Articles",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/product_overview.png",
                        "category": "TRAVEL",
                        "title": "Trip Planning for Total Beginners",
                        "description": "Essential tips and guides for first-time travelers. Learn how to plan your perfect trip from start to finish.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79"
                    },
                    {
                        "image_path": "images/process_diagram.png",
                        "category": "SURVIVAL",
                        "title": "7 Ways to Survive in the Desert",
                        "description": "Critical survival techniques for desert environments. Learn navigation, water finding, and safety measures.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79"
                    },
                    {
                        "image_path": "images/team_photo.png",
                        "category": "DESTINATIONS",
                        "title": "5 Amazing Travel Destinations",
                        "description": "Discover breathtaking locations around the world. From pristine beaches to majestic mountains.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79"
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_content_slide(
            "business_cards",
            "Business Insights",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/company_logo.png",
                        "category": "STRATEGY",
                        "title": "Digital Transformation Guide",
                        "description": "Comprehensive guide to modernizing your business with digital technologies and innovative approaches.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79"
                    },
                    {
                        "image_path": "images/chart_icon.png",
                        "category": "ANALYTICS",
                        "title": "Data-Driven Decision Making",
                        "description": "Learn how to leverage analytics and insights to make informed business decisions and drive growth.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79"
                    },
                    {
                        "image_path": "images/growth_icon.png",
                        "category": "GROWTH",
                        "title": "Scaling Your Business",
                        "description": "Strategic approaches to scaling your business while maintaining quality and customer satisfaction.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79"
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_thank_you_slide()
        .build())
    
    # Generate the presentation
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "card_demo_presentation.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run card demo"""
    print("=== Article Cards Demo ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("❌ Images directory not found. Please run create_simple_images.py first.")
            return
        
        # Create card demo
        output_file = create_card_demo()
        
        print(f"\n🎉 Successfully created card-based presentation!")
        print(f"📄 File: {output_file}")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"📊 Size: {file_size:.1f} KB")
        
        print("\n✨ Card features demonstrated:")
        print("  • Article-style card layout")
        print("  • Image, category, title, description structure")
        print("  • Horizontal card grid")
        print("  • Professional color scheme")
        print("  • Modern typography")
        print("  • Clean white cards on dark background")
        
    except Exception as e:
        print(f"❌ Error creating card demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 