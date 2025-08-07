"""
Badge Demo

This script demonstrates the badge system for cards with various styles and positions.
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


def create_badge_demo():
    """Create a demo presentation showcasing different badge styles"""
    print("Creating badge demo...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Badge System Demo",
            subtitle="Various Badge Styles and Positions",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_content_slide(
            "badge_positions",
            "Badge Positions",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/product_overview.png",
                        "category": "POSITION",
                        "title": "Top-Right Badge",
                        "description": "This card demonstrates a badge positioned in the top-right corner. Perfect for highlighting new or featured content.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "NEW",
                            "color": "#28a745",
                            "position": "top-right",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/process_diagram.png",
                        "category": "POSITION",
                        "title": "Top-Left Badge",
                        "description": "This card shows a badge in the top-left corner. Great for priority indicators or status labels.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "HOT",
                            "color": "#dc3545",
                            "position": "top-left",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/team_photo.png",
                        "category": "POSITION",
                        "title": "Bottom-Right Badge",
                        "description": "This card features a badge in the bottom-right corner. Ideal for category tags or completion status.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "COMPLETE",
                            "color": "#17a2b8",
                            "position": "bottom-right",
                            "size": "small"
                        }
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_content_slide(
            "badge_sizes",
            "Badge Sizes",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/company_logo.png",
                        "category": "SIZE",
                        "title": "Small Badge",
                        "description": "Small badges are perfect for subtle indicators like status or category tags. They don't overwhelm the content.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "SMALL",
                            "color": "#6c757d",
                            "position": "top-right",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/chart_icon.png",
                        "category": "SIZE",
                        "title": "Medium Badge",
                        "description": "Medium badges provide good visibility without being too prominent. Great for important but not critical information.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "MEDIUM",
                            "color": "#fd7e14",
                            "position": "top-right",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/growth_icon.png",
                        "category": "SIZE",
                        "title": "Large Badge",
                        "description": "Large badges are perfect for highlighting critical information or premium features that need maximum visibility.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "LARGE",
                            "color": "#dc3545",
                            "position": "top-right",
                            "size": "large"
                        }
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_content_slide(
            "badge_colors",
            "Badge Colors",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/idea_icon.png",
                        "category": "COLOR",
                        "title": "Success Badge",
                        "description": "Green badges are perfect for success indicators, completed tasks, or positive status messages.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "SUCCESS",
                            "color": "#28a745",
                            "position": "top-right",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/target_icon.png",
                        "category": "COLOR",
                        "title": "Warning Badge",
                        "description": "Yellow badges work well for warnings, pending items, or items that need attention.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "WARNING",
                            "color": "#ffc107",
                            "position": "top-right",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/results_summary.png",
                        "category": "COLOR",
                        "title": "Danger Badge",
                        "description": "Red badges are ideal for critical alerts, errors, or items that require immediate attention.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "badge": {
                            "text": "CRITICAL",
                            "color": "#dc3545",
                            "position": "top-right",
                            "size": "medium"
                        }
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
        "badge_demo.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run badge demo"""
    print("=== Badge System Demo ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("❌ Images directory not found. Please run create_simple_images.py first.")
            return
        
        # Create badge demo
        output_file = create_badge_demo()
        
        print(f"\n🎉 Successfully created badge demo presentation!")
        print(f"📄 File: {output_file}")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"📊 Size: {file_size:.1f} KB")
        
        print("\n✨ Badge features demonstrated:")
        print("  • Multiple badge positions (top-right, top-left, bottom-right, bottom-left)")
        print("  • Different badge sizes (small, medium, large)")
        print("  • Various badge colors (success, warning, danger, info)")
        print("  • Rounded badge corners matching card design")
        print("  • White text on colored backgrounds")
        print("  • Professional typography and spacing")
        
    except Exception as e:
        print(f"❌ Error creating badge demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 