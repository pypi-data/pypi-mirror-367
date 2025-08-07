#!/usr/bin/env python3
"""
Modern Styling Separated Demo

This script demonstrates how to use separated style and content templates
to create the modern styling demo presentation. It shows the complete workflow
from creating separate templates to merging them and generating the final presentation.
"""

import json
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from examples.merge_style_content import merge_style_and_content, validate_merged_config


def create_modern_styling_style_template():
    """Create the style template for modern styling demo"""
    style_template = {
        "presentation_style": {
            "id": "modern_styling_style",
            "name": "Modern Styling Demo",
            "description": "CSS-inspired design features with gradients, shadows, and modern typography",
            "theme": "modern_minimal",
            "slide_structure": [
                {
                    "id": "title_slide",
                    "type": "title",
                    "style": {
                        "background": "gradient",
                        "gradient_colors": ["#1f4e79", "#2c5aa0"],
                        "title_color": "#ffffff",
                        "subtitle_color": "#e0e0e0",
                        "title_font": "Segoe UI",
                        "title_font_size": 44,
                        "subtitle_font": "Segoe UI",
                        "subtitle_font_size": 24
                    },
                    "content_placeholders": {
                        "title": "string",
                        "subtitle": "string"
                    }
                },
                {
                    "id": "gradient_cards",
                    "type": "card_grid",
                    "style": {
                        "background": "solid",
                        "background_color": "#1f4e79",
                        "title_color": "#ffffff",
                        "title_font": "Segoe UI",
                        "title_font_size": 32,
                        "card_style": {
                            "background": "gradient",
                            "gradient_colors": ["#ffffff", "#f8f9fa"],
                            "rounded_corners": True,
                            "shadow": True,
                            "shadow_color": "#000000",
                            "shadow_opacity": 0.1,
                            "border": {
                                "style": "solid",
                                "width": 1,
                                "color": "#e0e0e0"
                            },
                            "category_color": "#6c757d",
                            "title_color": "#1f4e79",
                            "description_color": "#333333",
                            "category_font": "Segoe UI",
                            "category_font_size": 12,
                            "title_font": "Segoe UI",
                            "title_font_size": 18,
                            "description_font": "Segoe UI",
                            "description_font_size": 14,
                            "image_rounded": True
                        },
                        "badge_style": {
                            "font": "Segoe UI",
                            "font_size": 10,
                            "text_color": "#ffffff",
                            "positions": ["top-right", "top-left", "bottom-right", "bottom-left"],
                            "sizes": ["small", "medium", "large"],
                            "colors": {
                                "modern": "#2196f3",
                                "elegant": "#9c27b0",
                                "natural": "#4caf50"
                            }
                        },
                        "layout": "horizontal",
                        "card_spacing": 0.3
                    },
                    "content_placeholders": {
                        "title": "string",
                        "cards": "array_of_card_objects"
                    }
                },
                {
                    "id": "typography_cards",
                    "type": "card_grid",
                    "style": {
                        "background": "solid",
                        "background_color": "#1f4e79",
                        "title_color": "#ffffff",
                        "title_font": "Segoe UI",
                        "title_font_size": 32,
                        "card_style": {
                            "background": "gradient",
                            "gradient_colors": ["#ffffff", "#f8f9fa"],
                            "rounded_corners": True,
                            "shadow": True,
                            "shadow_color": "#000000",
                            "shadow_opacity": 0.1,
                            "border": {
                                "style": "solid",
                                "width": 1,
                                "color": "#e0e0e0"
                            },
                            "category_color": "#6c757d",
                            "title_color": "#1f4e79",
                            "description_color": "#333333",
                            "category_font": "Segoe UI",
                            "category_font_size": 12,
                            "title_font": "Segoe UI",
                            "title_font_size": 18,
                            "description_font": "Segoe UI",
                            "description_font_size": 14,
                            "image_rounded": True
                        },
                        "badge_style": {
                            "font": "Segoe UI",
                            "font_size": 10,
                            "text_color": "#ffffff",
                            "positions": ["top-right", "top-left", "bottom-right", "bottom-left"],
                            "sizes": ["small", "medium", "large"],
                            "colors": {
                                "custom": "#ff5722",
                                "pro": "#1976d2",
                                "creative": "#d32f2f"
                            }
                        },
                        "layout": "horizontal",
                        "card_spacing": 0.3
                    },
                    "content_placeholders": {
                        "title": "string",
                        "cards": "array_of_card_objects"
                    }
                },
                {
                    "id": "border_styles",
                    "type": "card_grid",
                    "style": {
                        "background": "solid",
                        "background_color": "#1f4e79",
                        "title_color": "#ffffff",
                        "title_font": "Segoe UI",
                        "title_font_size": 32,
                        "card_style": {
                            "background": "gradient",
                            "gradient_colors": ["#ffffff", "#f8f9fa"],
                            "rounded_corners": True,
                            "shadow": True,
                            "shadow_color": "#000000",
                            "shadow_opacity": 0.1,
                            "border": {
                                "style": "solid",
                                "width": 1,
                                "color": "#e0e0e0"
                            },
                            "category_color": "#6c757d",
                            "title_color": "#1f4e79",
                            "description_color": "#333333",
                            "category_font": "Segoe UI",
                            "category_font_size": 12,
                            "title_font": "Segoe UI",
                            "title_font_size": 18,
                            "description_font": "Segoe UI",
                            "description_font_size": 14,
                            "image_rounded": True
                        },
                        "badge_style": {
                            "font": "Segoe UI",
                            "font_size": 10,
                            "text_color": "#ffffff",
                            "positions": ["top-right", "top-left", "bottom-right", "bottom-left"],
                            "sizes": ["small", "medium", "large"],
                            "colors": {
                                "tech": "#00bcd4",
                                "playful": "#ff9800",
                                "premium": "#673ab7"
                            }
                        },
                        "layout": "horizontal",
                        "card_spacing": 0.3
                    },
                    "content_placeholders": {
                        "title": "string",
                        "cards": "array_of_card_objects"
                    }
                },
                {
                    "id": "thank_you",
                    "type": "thank_you",
                    "style": {
                        "background": "gradient",
                        "gradient_colors": ["#1f4e79", "#2c5aa0"],
                        "title_color": "#ffffff",
                        "subtitle_color": "#e0e0e0",
                        "contact_color": "#ffffff",
                        "title_font": "Segoe UI",
                        "title_font_size": 44,
                        "subtitle_font": "Segoe UI",
                        "subtitle_font_size": 24,
                        "contact_font": "Segoe UI",
                        "contact_font_size": 18
                    },
                    "content_placeholders": {
                        "title": "string",
                        "subtitle": "string",
                        "contact": "string"
                    }
                }
            ],
            "global_styling": {
                "fonts": {
                    "heading": "Segoe UI",
                    "body": "Segoe UI",
                    "category": "Segoe UI",
                    "title": "Segoe UI",
                    "description": "Segoe UI"
                },
                "colors": {
                    "primary": "#1f4e79",
                    "secondary": "#6c757d",
                    "accent": "#007bff",
                    "background": "#ffffff",
                    "text": "#333333"
                },
                "spacing": {
                    "slide_padding": 0.5,
                    "element_margin": 0.25,
                    "card_padding": 0.3
                }
            }
        }
    }
    
    return style_template


def create_modern_styling_content_template():
    """Create the content template for modern styling demo"""
    content_template = {
        "presentation_content": {
            "id": "modern_styling_demo",
            "title": "Modern Styling Demo",
            "subtitle": "CSS-Inspired Design Features",
            "author": "Demo User",
            "company": "Demo Company",
            "date": "2024",
            "slides": [
                {
                    "id": "title_slide",
                    "content": {
                        "title": "Modern Styling Demo",
                        "subtitle": "CSS-Inspired Design Features"
                    }
                },
                {
                    "id": "gradient_cards",
                    "content": {
                        "title": "Gradient Backgrounds",
                        "cards": [
                            {
                                "image_path": "images/product_overview.png",
                                "category": "GRADIENT",
                                "title": "Linear Gradient",
                                "description": "Beautiful linear gradient from white to light blue, creating a modern and clean appearance.",
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
                        ]
                    }
                },
                {
                    "id": "typography_cards",
                    "content": {
                        "title": "Modern Typography",
                        "cards": [
                            {
                                "image_path": "images/idea_icon.png",
                                "category": "TYPOGRAPHY",
                                "title": "Custom Fonts & Colors",
                                "description": "Advanced typography with custom fonts, sizes, and colors for maximum visual impact.",
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
                        ]
                    }
                },
                {
                    "id": "border_styles",
                    "content": {
                        "title": "Border Styles & Effects",
                        "cards": [
                            {
                                "image_path": "images/chart_icon.png",
                                "category": "BORDERS",
                                "title": "Dashed Borders",
                                "description": "Dashed borders create a modern, tech-inspired look perfect for digital products.",
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
                        ]
                    }
                },
                {
                    "id": "thank_you",
                    "content": {
                        "title": "Thank You",
                        "subtitle": "Modern Styling Features",
                        "contact": "demo@company.com"
                    }
                }
            ]
        }
    }
    
    return content_template


def demonstrate_separated_templates_workflow():
    """Demonstrate the complete workflow of using separated templates"""
    print("🎨 **Modern Styling Separated Templates Demo**")
    print("=" * 60)
    print()
    
    print("📋 **Step 1: Create Style Template**")
    style_template = create_modern_styling_style_template()
    style_file = "examples/modern_styling_style_demo.json"
    
    with open(style_file, 'w', encoding='utf-8') as f:
        json.dump(style_template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created style template: {style_file}")
    print(f"   • Theme: {style_template['presentation_style']['theme']}")
    print(f"   • Slides: {len(style_template['presentation_style']['slide_structure'])}")
    print(f"   • Features: Gradients, shadows, modern typography")
    print()
    
    print("📋 **Step 2: Create Content Template**")
    content_template = create_modern_styling_content_template()
    content_file = "examples/modern_styling_content_demo.json"
    
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content_template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created content template: {content_file}")
    print(f"   • Title: {content_template['presentation_content']['title']}")
    print(f"   • Author: {content_template['presentation_content']['author']}")
    print(f"   • Slides: {len(content_template['presentation_content']['slides'])}")
    print(f"   • Features: Gradient examples, typography, border styles")
    print()
    
    print("📋 **Step 3: Merge Templates**")
    merged_config = merge_style_and_content(style_template, content_template)
    merged_file = "examples/modern_styling_merged_demo.json"
    
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(merged_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Merged templates: {merged_file}")
    
    # Validate the merged configuration
    if validate_merged_config(merged_config):
        print("✅ Merged configuration is valid")
        
        # Print summary
        presentation = merged_config['presentations'][0]
        slides = presentation['slides']
        
        print(f"\n📊 **Merged Configuration Summary:**")
        print(f"   • Presentation: {presentation['title']}")
        print(f"   • Author: {presentation['author']}")
        print(f"   • Company: {presentation['company']}")
        print(f"   • Theme: {presentation['theme']}")
        print(f"   • Slides: {len(slides)}")
        
        # Count slide types
        slide_types = {}
        for slide in slides:
            slide_type = slide['type']
            slide_types[slide_type] = slide_types.get(slide_type, 0) + 1
        
        print(f"   • Slide Types:")
        for slide_type, count in slide_types.items():
            print(f"     - {slide_type}: {count}")
        
        print(f"\n🚀 **Ready to generate presentation:**")
        print(f"   ppt-template generate {merged_file}")
        
    else:
        print("❌ Merged configuration validation failed")
        return False
    
    print()
    print("🎯 **Benefits of Separated Templates:**")
    print("   ✅ Style template focuses on visual design and structure")
    print("   ✅ Content template focuses on text, images, and data")
    print("   ✅ Easy to reuse styles with different content")
    print("   ✅ Easy to reuse content with different styles")
    print("   ✅ Clear separation of concerns")
    print("   ✅ Better maintainability and flexibility")
    
    print()
    print("📁 **Generated Files:**")
    print(f"   • Style Template: {style_file}")
    print(f"   • Content Template: {content_file}")
    print(f"   • Merged Configuration: {merged_file}")
    
    return True


def main():
    """Main function to demonstrate separated templates workflow"""
    print("=== Modern Styling Separated Templates Demo ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("⚠️  Images directory not found. Creating placeholder images...")
            # Create images directory if it doesn't exist
            os.makedirs(images_dir, exist_ok=True)
            print("✅ Created images directory")
        
        # Demonstrate the workflow
        success = demonstrate_separated_templates_workflow()
        
        if success:
            print("\n🎉 **Demo completed successfully!**")
            print("\n✨ **Modern styling features demonstrated:**")
            print("  • Gradient backgrounds (linear, radial, vertical)")
            print("  • Shadow effects for depth and dimension")
            print("  • Border styles (solid, dashed, dotted)")
            print("  • Custom typography (fonts, sizes, colors)")
            print("  • Line spacing and text formatting")
            print("  • Color schemes and visual hierarchy")
            print("  • Professional and creative design options")
            
            print("\n🔧 **Next Steps:**")
            print("  1. Generate presentation: ppt-template generate examples/modern_styling_merged_demo.json")
            print("  2. Modify style template for different visual themes")
            print("  3. Modify content template for different topics")
            print("  4. Combine different style and content templates")
            
        else:
            print("\n❌ Demo failed. Please check the error messages above.")
            
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 