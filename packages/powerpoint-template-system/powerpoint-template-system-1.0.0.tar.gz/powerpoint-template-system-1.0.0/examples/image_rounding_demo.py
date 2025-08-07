"""
Image Rounding Demo

This script demonstrates the image rounding options for cards.
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


def create_image_rounding_demo():
    """Create a demo presentation showcasing different image rounding options"""
    print("Creating image rounding demo...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Image Rounding Demo",
            subtitle="Different Image Border Options",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_content_slide(
            "image_rounding_options",
            "Image Rounding Options",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/product_overview.png",
                        "category": "ROUNDED CARD + ROUNDED IMAGE",
                        "title": "Both Rounded",
                        "description": "This card has rounded corners and the image area is also rounded, creating a fully unified design.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "UNIFIED",
                            "color": "#28a745",
                            "position": "top-right",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/process_diagram.png",
                        "category": "ROUNDED CARD + SQUARE IMAGE",
                        "title": "Mixed Design",
                        "description": "This card has rounded corners but the image area is square, creating a mixed design approach.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "image_rounded": False,
                        "badge": {
                            "text": "MIXED",
                            "color": "#ffc107",
                            "position": "top-left",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/team_photo.png",
                        "category": "SQUARE CARD + SQUARE IMAGE",
                        "title": "Classic Design",
                        "description": "This card has square corners and the image area is also square, creating a classic, structured design.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False,
                        "image_rounded": False,
                        "badge": {
                            "text": "CLASSIC",
                            "color": "#6c757d",
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
            "image_rounding_comparison",
            "Image Rounding Comparison",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/idea_icon.png",
                        "category": "MODERN",
                        "title": "Fully Rounded Design",
                        "description": "Both card and image have rounded corners for a modern, friendly appearance that feels approachable.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "MODERN",
                            "color": "#20c997",
                            "position": "top-right",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/target_icon.png",
                        "category": "HYBRID",
                        "title": "Hybrid Approach",
                        "description": "Rounded card with square image creates visual interest while maintaining some structure.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "image_rounded": False,
                        "badge": {
                            "text": "HYBRID",
                            "color": "#fd7e14",
                            "position": "top-left",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/results_summary.png",
                        "category": "PROFESSIONAL",
                        "title": "Professional Design",
                        "description": "Square card and square image create a clean, professional appearance suitable for corporate use.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False,
                        "image_rounded": False,
                        "badge": {
                            "text": "PRO",
                            "color": "#6f42c1",
                            "position": "bottom-right",
                            "size": "medium"
                        }
                    }
                ],
                "layout": "horizontal",
                "background_color": "#1f4e79",
                "card_spacing": 0.3
            }
        )
        .add_content_slide(
            "image_rounding_use_cases",
            "Image Rounding Use Cases",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/chart_icon.png",
                        "category": "CREATIVE",
                        "title": "Creative Projects",
                        "description": "Fully rounded design is perfect for creative projects, portfolios, and modern applications.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "CREATIVE",
                            "color": "#e83e8c",
                            "position": "top-right",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/growth_icon.png",
                        "category": "BUSINESS",
                        "title": "Business Applications",
                        "description": "Mixed design works well for business applications where you want modern appeal with some structure.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": True,
                        "image_rounded": False,
                        "badge": {
                            "text": "BUSINESS",
                            "color": "#17a2b8",
                            "position": "top-left",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/company_logo.png",
                        "category": "CORPORATE",
                        "title": "Corporate Presentations",
                        "description": "Square design is ideal for corporate presentations, financial reports, and formal documents.",
                        "card_color": "#ffffff",
                        "category_color": "#6c757d",
                        "title_color": "#1f4e79",
                        "rounded_corners": False,
                        "image_rounded": False,
                        "badge": {
                            "text": "CORPORATE",
                            "color": "#6c757d",
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
        .add_thank_you_slide()
        .build())
    
    # Generate the presentation
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "image_rounding_demo.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run image rounding demo"""
    print("=== Image Rounding Demo ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("❌ Images directory not found. Please run create_simple_images.py first.")
            return
        
        # Create image rounding demo
        output_file = create_image_rounding_demo()
        
        print(f"\n🎉 Successfully created image rounding demo presentation!")
        print(f"📄 File: {output_file}")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"📊 Size: {file_size:.1f} KB")
        
        print("\n✨ Image rounding features demonstrated:")
        print("  • Rounded card + Rounded image (fully unified)")
        print("  • Rounded card + Square image (mixed design)")
        print("  • Square card + Square image (classic design)")
        print("  • Independent image rounding control")
        print("  • Different use cases for each style")
        print("  • Professional color-coded placeholders")
        
    except Exception as e:
        print(f"❌ Error creating image rounding demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 