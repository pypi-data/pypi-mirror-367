"""
Modern Styling Demo

This script demonstrates modern CSS-inspired styling features for cards.
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


def create_modern_styling_demo():
    """Create a demo presentation showcasing modern styling features"""
    print("Creating modern styling demo...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Modern Styling Demo",
            subtitle="CSS-Inspired Design Features",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_content_slide(
            "gradient_cards",
            "Gradient Backgrounds",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/product_overview.png",
                        "category": "GRADIENT",
                        "title": "Linear Gradient",
                        "description": "Beautiful linear gradient from white to light blue, creating a modern and clean appearance.",
                        "card_color": "#ffffff",
                        "gradient": {
                            "type": "linear",
                            "colors": ["#ffffff", "#e3f2fd"],
                            "direction": "horizontal"
                        },
                        "shadow": True,
                        "border_style": "solid",
                        "border_width": 2,
                        "border_color": "#2196f3",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "MODERN",
                            "color": "#2196f3",
                            "position": "top-right",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/process_diagram.png",
                        "category": "GRADIENT",
                        "title": "Radial Gradient",
                        "description": "Elegant radial gradient from center outward, perfect for highlighting important content.",
                        "card_color": "#ffffff",
                        "gradient": {
                            "type": "radial",
                            "colors": ["#f3e5f5", "#e1bee7"]
                        },
                        "shadow": True,
                        "border_style": "dashed",
                        "border_width": 1,
                        "border_color": "#9c27b0",
                        "rounded_corners": True,
                        "image_rounded": False,
                        "badge": {
                            "text": "ELEGANT",
                            "color": "#9c27b0",
                            "position": "top-left",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/team_photo.png",
                        "category": "GRADIENT",
                        "title": "Vertical Gradient",
                        "description": "Vertical gradient creates depth and visual interest while maintaining readability.",
                        "card_color": "#ffffff",
                        "gradient": {
                            "type": "linear",
                            "colors": ["#e8f5e8", "#c8e6c9"],
                            "direction": "vertical"
                        },
                        "shadow": True,
                        "border_style": "dotted",
                        "border_width": 1,
                        "border_color": "#4caf50",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "NATURAL",
                            "color": "#4caf50",
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
            "typography_cards",
            "Modern Typography",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/idea_icon.png",
                        "category": "TYPOGRAPHY",
                        "title": "Custom Fonts & Colors",
                        "description": "Advanced typography with custom fonts, sizes, and colors for maximum visual impact.",
                        "card_color": "#ffffff",
                        "shadow": True,
                        "rounded_corners": True,
                        "image_rounded": True,
                        "category_font": "Arial",
                        "category_font_size": 12,
                        "category_color": "#ff5722",
                        "title_font": "Calibri",
                        "title_font_size": 16,
                        "title_color": "#2e7d32",
                        "description_font": "Verdana",
                        "description_font_size": 11,
                        "description_color": "#424242",
                        "line_spacing": 1.4,
                        "badge": {
                            "text": "CUSTOM",
                            "color": "#ff5722",
                            "position": "top-right",
                            "size": "medium"
                        }
                    },
                    {
                        "image_path": "images/target_icon.png",
                        "category": "TYPOGRAPHY",
                        "title": "Professional Typography",
                        "description": "Clean, professional typography with optimal spacing and contrast for business presentations.",
                        "card_color": "#ffffff",
                        "shadow": True,
                        "rounded_corners": True,
                        "image_rounded": False,
                        "category_font": "Segoe UI",
                        "category_font_size": 10,
                        "category_color": "#1976d2",
                        "title_font": "Segoe UI",
                        "title_font_size": 14,
                        "title_color": "#1565c0",
                        "description_font": "Segoe UI",
                        "description_font_size": 10,
                        "description_color": "#424242",
                        "line_spacing": 1.3,
                        "badge": {
                            "text": "PRO",
                            "color": "#1976d2",
                            "position": "top-left",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/results_summary.png",
                        "category": "TYPOGRAPHY",
                        "title": "Creative Typography",
                        "description": "Bold, creative typography with larger fonts and vibrant colors for maximum impact.",
                        "card_color": "#ffffff",
                        "shadow": True,
                        "rounded_corners": True,
                        "image_rounded": True,
                        "category_font": "Arial Black",
                        "category_font_size": 14,
                        "category_color": "#d32f2f",
                        "title_font": "Impact",
                        "title_font_size": 18,
                        "title_color": "#c62828",
                        "description_font": "Arial",
                        "description_font_size": 12,
                        "description_color": "#212121",
                        "line_spacing": 1.5,
                        "badge": {
                            "text": "CREATIVE",
                            "color": "#d32f2f",
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
            "border_styles",
            "Border Styles & Effects",
            "card_grid",
            {
                "cards": [
                    {
                        "image_path": "images/chart_icon.png",
                        "category": "BORDERS",
                        "title": "Dashed Borders",
                        "description": "Dashed borders create a modern, tech-inspired look perfect for digital products.",
                        "card_color": "#ffffff",
                        "shadow": True,
                        "border_style": "dashed",
                        "border_width": 2,
                        "border_color": "#00bcd4",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "TECH",
                            "color": "#00bcd4",
                            "position": "top-right",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/growth_icon.png",
                        "category": "BORDERS",
                        "title": "Dotted Borders",
                        "description": "Dotted borders add a playful, creative touch while maintaining professionalism.",
                        "card_color": "#ffffff",
                        "shadow": True,
                        "border_style": "dotted",
                        "border_width": 1,
                        "border_color": "#ff9800",
                        "rounded_corners": True,
                        "image_rounded": False,
                        "badge": {
                            "text": "PLAYFUL",
                            "color": "#ff9800",
                            "position": "top-left",
                            "size": "small"
                        }
                    },
                    {
                        "image_path": "images/company_logo.png",
                        "category": "BORDERS",
                        "title": "Thick Solid Borders",
                        "description": "Thick solid borders create a bold, confident appearance for premium content.",
                        "card_color": "#ffffff",
                        "shadow": True,
                        "border_style": "solid",
                        "border_width": 3,
                        "border_color": "#673ab7",
                        "rounded_corners": True,
                        "image_rounded": True,
                        "badge": {
                            "text": "PREMIUM",
                            "color": "#673ab7",
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
        .add_thank_you_slide()
        .build())
    
    # Generate the presentation
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "modern_styling_demo.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run modern styling demo"""
    print("=== Modern Styling Demo ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("❌ Images directory not found. Please run create_simple_images.py first.")
            return
        
        # Create modern styling demo
        output_file = create_modern_styling_demo()
        
        print(f"\n🎉 Successfully created modern styling demo presentation!")
        print(f"📄 File: {output_file}")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"📊 Size: {file_size:.1f} KB")
        
        print("\n✨ Modern styling features demonstrated:")
        print("  • Gradient backgrounds (linear, radial, vertical)")
        print("  • Shadow effects for depth and dimension")
        print("  • Border styles (solid, dashed, dotted)")
        print("  • Custom typography (fonts, sizes, colors)")
        print("  • Line spacing and text formatting")
        print("  • Color schemes and visual hierarchy")
        print("  • Professional and creative design options")
        
    except Exception as e:
        print(f"❌ Error creating modern styling demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 