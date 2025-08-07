"""
Card Comparison Demo

This script demonstrates both rounded and square cards with proper text wrapping.
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


def create_card_comparison_demo():
    """Create a demo presentation comparing rounded and square cards"""
    print("Creating card comparison demo...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Card Comparison Demo",
            subtitle="Rounded vs Square Cards",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_content_slide(
            "rounded_cards",
            "Rounded Corner Cards",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/product_overview.png",
                        "category": "DESIGN",
                        "title": "Modern Rounded Card Design",
                        "description": "This card demonstrates the modern rounded corner design with proper text wrapping. The text will automatically wrap to fit within the card boundaries, ensuring all content is visible and properly formatted.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True
                    },
                    {
                        "image_path": "images/process_diagram.png",
                        "category": "FEATURES",
                        "title": "Text Wrapping and Rounded Borders",
                        "description": "Long descriptions like this one will automatically wrap to multiple lines, ensuring all text is visible and readable. The rounded corners give a modern, friendly appearance.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True
                    },
                    {
                        "image_path": "images/team_photo.png",
                        "category": "STYLING",
                        "title": "Professional Card Styling",
                        "description": "Each card can have custom colors, fonts, and styling while maintaining consistent layout and proper text wrapping for optimal readability.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_content_slide(
            "square_cards",
            "Square Corner Cards",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/company_logo.png",
                        "category": "DESIGN",
                        "title": "Classic Square Card Design",
                        "description": "This card demonstrates the classic square corner design with proper text wrapping. The text will automatically wrap to fit within the card boundaries, ensuring all content is visible and properly formatted.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False
                    },
                    {
                        "image_path": "images/chart_icon.png",
                        "category": "FEATURES",
                        "title": "Text Wrapping and Square Borders",
                        "description": "Long descriptions like this one will automatically wrap to multiple lines, ensuring all text is visible and readable. The square corners give a classic, professional appearance.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False
                    },
                    {
                        "image_path": "images/growth_icon.png",
                        "category": "STYLING",
                        "title": "Professional Card Styling",
                        "description": "Each card can have custom colors, fonts, and styling while maintaining consistent layout and proper text wrapping for optimal readability.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_content_slide(
            "mixed_cards",
            "Mixed Card Styles",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/idea_icon.png",
                        "category": "ROUNDED",
                        "title": "Rounded Corner Card",
                        "description": "This card has rounded corners for a modern, friendly appearance. Perfect for creative and innovative content that needs a softer, more approachable feel.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True
                    },
                    {
                        "image_path": "images/target_icon.png",
                        "category": "SQUARE",
                        "title": "Square Corner Card",
                        "description": "This card has square corners for a classic, professional appearance. Perfect for business and corporate content that needs a more formal, structured feel.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False
                    },
                    {
                        "image_path": "images/results_summary.png",
                        "category": "ROUNDED",
                        "title": "Another Rounded Card",
                        "description": "You can mix and match card styles on the same slide. This allows for creative layouts that combine different visual styles for maximum impact.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True
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
        "card_comparison_demo.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run card comparison demo"""
    print("=== Card Comparison Demo ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("❌ Images directory not found. Please run create_simple_images.py first.")
            return
        
        # Create card comparison demo
        output_file = create_card_comparison_demo()
        
        print(f"\n🎉 Successfully created card comparison presentation!")
        print(f"📄 File: {output_file}")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"📊 Size: {file_size:.1f} KB")
        
        print("\n✨ Features demonstrated:")
        print("  • Rounded corner cards (modern design)")
        print("  • Square corner cards (classic design)")
        print("  • Mixed card styles on same slide")
        print("  • Proper text wrapping for all content")
        print("  • Custom card colors and styling")
        print("  • Professional typography and spacing")
        
    except Exception as e:
        print(f"❌ Error creating card comparison demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 