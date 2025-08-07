"""
Image Demo Template for PowerPoint

This example demonstrates how to create presentations with images
using the PowerPoint template system.
"""

import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.powerpoint_templates import (
    BusinessDSLBuilder, 
    BusinessTheme, 
    EnhancedVisualGenerator,
    BusinessTemplateExamples
)


def create_image_demo_presentation():
    """Create a presentation that demonstrates image usage"""
    print("Creating image demo presentation...")
    
    # Build presentation using DSL with images
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Image Demo Presentation",
            subtitle="Demonstrating Image Integration",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_content_slide(
            "company_overview",
            "Company Overview",
            "image_with_text",
            {
                "image_path": "images/company_logo.png",
                "image_position": "left",
                "text_content": [
                    "• Established in 2020",
                    "• 50+ employees worldwide",
                    "• $10M annual revenue",
                    "• Focus on innovation"
                ],
                "image_width": 2.5,
                "image_height": 2.0
            }
        )
        .add_content_slide(
            "product_demo",
            "Product Overview",
            "image_focus",
            {
                "image_path": "images/product_overview.png",
                "image_width": 6.0,
                "image_height": 4.0,
                "caption": "Our flagship product in action"
            }
        )
        .add_content_slide(
            "team_intro",
            "Meet Our Team",
            "image_grid",
            {
                "images": [
                    {"path": "images/team_photo.png", "caption": "Leadership Team"},
                    {"path": "images/idea_icon.png", "caption": "Innovation"},
                    {"path": "images/target_icon.png", "caption": "Goals"}
                ],
                "layout": "2x2"
            }
        )
        .add_content_slide(
            "process_flow",
            "Our Process",
            "image_with_text",
            {
                "image_path": "images/process_diagram.png",
                "image_position": "right",
                "text_content": [
                    "1. Discovery Phase",
                    "2. Design & Development",
                    "3. Testing & Quality",
                    "4. Deployment",
                    "5. Support & Maintenance"
                ],
                "image_width": 3.0,
                "image_height": 2.5
            }
        )
        .add_content_slide(
            "results_chart",
            "Results & Metrics",
            "mixed_content",
            {
                "chart_data": {
                    "chart_type": "bar",
                    "data": [85, 92, 78, 95, 88],
                    "labels": ["Q1", "Q2", "Q3", "Q4", "Target"],
                    "title": "Quarterly Performance"
                },
                "image_path": "images/sample_chart.png",
                "image_position": "bottom",
                "image_width": 4.0,
                "image_height": 2.0
            }
        )
        .add_content_slide(
            "summary",
            "Summary",
            "image_with_text",
            {
                "image_path": "images/results_summary.png",
                "image_position": "center",
                "text_content": [
                    "• Achieved 90% customer satisfaction",
                    "• Increased efficiency by 25%",
                    "• Reduced costs by 15%",
                    "• Expanded to 3 new markets"
                ],
                "image_width": 3.5,
                "image_height": 2.5
            }
        )
        .add_thank_you_slide(
            contact_info={
                "email": "demo@company.com",
                "website": "www.company.com",
                "phone": "+1 (555) 123-4567"
            }
        )
        .build())
    
    # Generate the presentation
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "image_demo_presentation.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def create_icon_based_presentation():
    """Create a presentation using icon-style images"""
    print("Creating icon-based presentation...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Icon-Based Presentation",
            subtitle="Using Icons for Visual Impact",
            author="Demo User",
            company="Demo Company"
        )
        .set_theme(BusinessTheme.STARTUP_VIBRANT)
        .add_title_slide()
        .add_content_slide(
            "key_metrics",
            "Key Metrics",
            "icon_grid",
            {
                "icons": [
                    {"path": "images/chart_icon.png", "title": "Analytics", "description": "Data-driven insights"},
                    {"path": "images/growth_icon.png", "title": "Growth", "description": "25% YoY increase"},
                    {"path": "images/idea_icon.png", "title": "Innovation", "description": "New product features"},
                    {"path": "images/target_icon.png", "title": "Goals", "description": "Achieved 95% of targets"}
                ],
                "layout": "2x2"
            }
        )
        .add_content_slide(
            "strategy",
            "Our Strategy",
            "icon_timeline",
            {
                "timeline_items": [
                    {"icon": "images/idea_icon.png", "phase": "Phase 1", "title": "Research", "description": "Market analysis"},
                    {"icon": "images/target_icon.png", "phase": "Phase 2", "title": "Planning", "description": "Strategy development"},
                    {"icon": "images/growth_icon.png", "phase": "Phase 3", "title": "Execution", "description": "Implementation"},
                    {"icon": "images/chart_icon.png", "phase": "Phase 4", "title": "Evaluation", "description": "Results measurement"}
                ]
            }
        )
        .add_thank_you_slide()
        .build())
    
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "icon_based_presentation.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run image demo examples"""
    print("=== PowerPoint Template System - Image Demo Examples ===\n")
    
    try:
        # Check if images exist
        images_dir = "images"
        if not os.path.exists(images_dir):
            print("❌ Images directory not found. Please run create_simple_images.py first.")
            return
        
        # Create examples
        files_created = []
        
        files_created.append(create_image_demo_presentation())
        files_created.append(create_icon_based_presentation())
        
        print(f"\n🎉 Successfully created {len(files_created)} image-based presentations!")
        print("\nFiles created:")
        for file in files_created:
            if os.path.exists(file):
                file_size = os.path.getsize(file) / 1024
                print(f"  📄 {file} ({file_size:.1f} KB)")
        
        print("\n✨ Image features demonstrated:")
        print("  • Image integration in slides")
        print("  • Multiple image layouts (left, right, center)")
        print("  • Image grids and icon displays")
        print("  • Mixed content (text + images)")
        print("  • Icon-based visual elements")
        print("  • Professional image positioning")
        
    except Exception as e:
        print(f"❌ Error creating image examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 