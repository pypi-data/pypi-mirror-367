"""
Quick Start Example for PowerPoint Template System

This example demonstrates how to create a professional business presentation
using the template system with minimal code.
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


def create_simple_presentation():
    """Create a simple business presentation"""
    print("Creating simple business presentation...")
    
    # Build presentation using DSL
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Quick Start Demo",
            subtitle="PowerPoint Template System Example",
            author="Demo User",
            company="Demo Company",
            date="2024"
        )
        .set_theme(BusinessTheme.MODERN_MINIMAL)
        .add_title_slide()
        .add_agenda_slide("agenda", [
            "Introduction",
            "Key Features",
            "Benefits",
            "Next Steps"
        ])
        .add_content_slide(
            "features",
            "Key Features",
            "bullet_list",
            {
                "items": [
                    "Professional business templates",
                    "16:9 widescreen format",
                    "Modern visual styling",
                    "Actual charts and data visualization",
                    "Modular component system",
                    "Easy-to-use DSL"
                ]
            }
        )
        .add_content_slide(
            "benefits",
            "Benefits",
            "bullet_list",
            {
                "items": [
                    {"text": "Faster Development", "level": 0},
                    {"text": "60-70% reduction in creation time", "level": 1},
                    {"text": "Professional Quality", "level": 0},
                    {"text": "Corporate-grade visual appearance", "level": 1},
                    {"text": "Consistency", "level": 0},
                    {"text": "Standardized branding and layouts", "level": 1}
                ]
            }
        )
        .add_thank_you_slide(
            contact_info={
                "email": "demo@company.com",
                "website": "www.company.com"
            }
        )
        .build())
    
    # Generate the presentation
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "quick_start_demo.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def create_chart_example():
    """Create a presentation with actual charts"""
    print("Creating presentation with charts...")
    
    presentation = (BusinessDSLBuilder()
        .set_metadata(
            title="Chart Demo",
            subtitle="Data Visualization Example",
            author="Demo User",
            company="Demo Company"
        )
        .set_theme(BusinessTheme.CORPORATE_BLUE)
        .add_title_slide()
        .add_content_slide(
            "revenue_chart",
            "Revenue Growth",
            "chart",
            {
                "chart_type": "line",
                "data": [100, 125, 150, 180, 220],
                "labels": ["2020", "2021", "2022", "2023", "2024"],
                "title": "Annual Revenue (in millions)"
            }
        )
        .add_content_slide(
            "market_share",
            "Market Share Analysis",
            "chart",
            {
                "chart_type": "bar",
                "data": [35, 28, 22, 15],
                "labels": ["Company A", "Company B", "Company C", "Others"],
                "title": "Market Share Distribution"
            }
        )
        .add_thank_you_slide()
        .build())
    
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        presentation, 
        "chart_demo.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def create_business_template_example():
    """Create presentation using pre-built business template"""
    print("Creating presentation from business template...")
    
    # Use pre-built quarterly business review template
    qbr_presentation = BusinessTemplateExamples.create_quarterly_business_review()
    
    generator = EnhancedVisualGenerator()
    output_file = generator.create_presentation_from_dsl(
        qbr_presentation, 
        "business_template_example.pptx"
    )
    
    print(f"✅ Created: {output_file}")
    return output_file


def main():
    """Run all examples"""
    print("=== PowerPoint Template System - Quick Start Examples ===\n")
    
    try:
        # Create examples
        files_created = []
        
        files_created.append(create_simple_presentation())
        files_created.append(create_chart_example())
        files_created.append(create_business_template_example())
        
        print(f"\n🎉 Successfully created {len(files_created)} example presentations!")
        print("\nFiles created:")
        for file in files_created:
            if os.path.exists(file):
                file_size = os.path.getsize(file) / 1024
                print(f"  📄 {file} ({file_size:.1f} KB)")
        
        print("\n✨ Features demonstrated:")
        print("  • Business-focused DSL")
        print("  • 16:9 widescreen format")
        print("  • Professional visual styling")
        print("  • Actual chart generation")
        print("  • Pre-built business templates")
        print("  • Modern component architecture")
        
    except Exception as e:
        print(f"❌ Error creating examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()