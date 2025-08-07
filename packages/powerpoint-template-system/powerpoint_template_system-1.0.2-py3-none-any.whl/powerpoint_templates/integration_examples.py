"""
Integration Examples for Template System with Existing PowerPoint Generator

This module shows how to integrate the new template system with your existing
pptx_generator_enhanced.py code.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import your existing generator (assuming it's available)
# from pptx_generator_enhanced import EnhancedPPTXGenerator

# Import our new systems
from .template_system_design import (
    BusinessPresentationTemplate, BusinessTheme, TemplateLibrary,
    StyleConfig, HeaderConfig, FooterConfig, ContentConfig
)
from .enhanced_business_dsl import (
    BusinessPresentationDSL, BusinessDSLBuilder, BusinessSlide,
    SlideHeader, SlideContent, SlideFooter
)
from .modular_components import (
    ComponentLayout, LayoutLibrary, HeaderComponent, FooterComponent,
    ContentComponent, ComponentBounds, ComponentStyle
)


class EnhancedTemplateGenerator:
    """
    Enhanced generator that integrates template system with existing functionality
    """
    
    def __init__(self, base_generator=None):
        """Initialize with optional base generator for backward compatibility"""
        self.base_generator = base_generator
        self.template_library = {}
        self.component_library = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default business templates"""
        self.template_library = {
            'executive_summary': TemplateLibrary.get_executive_summary_template(),
            'sales_pitch': TemplateLibrary.get_sales_pitch_template(),
            'financial_report': TemplateLibrary.get_financial_report_template()
        }
        
        self.component_library = {
            'standard_business': LayoutLibrary.create_standard_business_layout(),
            'executive': LayoutLibrary.create_executive_layout(),
            'two_column': LayoutLibrary.create_two_column_layout()
        }
    
    def create_presentation_from_dsl(self, dsl: BusinessPresentationDSL) -> str:
        """Create presentation from business DSL"""
        # Get the appropriate template
        template = self.template_library.get(dsl.template_name)
        if not template:
            template = TemplateLibrary.get_executive_summary_template()
        
        # Convert DSL to your existing format if needed
        presentation_data = self._convert_dsl_to_legacy_format(dsl)
        
        # Generate presentation using template
        output_path = f"{dsl.title.replace(' ', '_').lower()}.pptx"
        
        # Here you would integrate with your existing generator
        # if self.base_generator:
        #     return self.base_generator.generate_presentation(presentation_data, output_path)
        
        return output_path
    
    def _convert_dsl_to_legacy_format(self, dsl: BusinessPresentationDSL) -> Dict[str, Any]:
        """Convert new DSL format to your existing generator format"""
        presentation_data = {
            'metadata': {
                'title': dsl.title,
                'subtitle': dsl.subtitle,
                'author': dsl.author,
                'company': dsl.company,
                'date': dsl.date
            },
            'theme': dsl.theme.value,
            'slides': []
        }
        
        for slide in dsl.slides:
            slide_data = {
                'slide_id': slide.slide_id,
                'slide_type': slide.slide_type,
                'layout': slide.layout.value,
                'content': slide.content.data if slide.content else {},
                'header': self._convert_header(slide.header) if slide.header else None,
                'footer': self._convert_footer(slide.footer) if slide.footer else None
            }
            presentation_data['slides'].append(slide_data)
        
        return presentation_data
    
    def _convert_header(self, header: SlideHeader) -> Dict[str, Any]:
        """Convert header to legacy format"""
        return {
            'title': header.title,
            'subtitle': header.subtitle,
            'show_logo': header.show_logo,
            'show_date': header.show_date
        }
    
    def _convert_footer(self, footer: SlideFooter) -> Dict[str, Any]:
        """Convert footer to legacy format"""
        return {
            'show_page_number': footer.show_page_number,
            'show_company_name': footer.show_company_name,
            'show_confidentiality': footer.show_confidentiality,
            'custom_text': footer.custom_text
        }
    
    def create_custom_template(self, template_name: str, theme: BusinessTheme,
                             header_config: HeaderConfig = None,
                             footer_config: FooterConfig = None,
                             content_config: ContentConfig = None) -> BusinessPresentationTemplate:
        """Create a custom business template"""
        template = BusinessPresentationTemplate(theme, template_name)
        
        # Customize template based on provided configurations
        if header_config or footer_config or content_config:
            # Create custom slide templates with the provided configurations
            pass  # Implementation would customize the template
        
        self.template_library[template_name] = template
        return template
    
    def export_template_config(self, template_name: str, output_path: str) -> bool:
        """Export template configuration for reuse"""
        template = self.template_library.get(template_name)
        if not template:
            return False
        
        template.export_config(output_path)
        return True
    
    def load_template_config(self, config_path: str) -> Optional[BusinessPresentationTemplate]:
        """Load template from configuration file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            theme = BusinessTheme(config_data['theme'])
            template = BusinessPresentationTemplate(theme, config_data['template_name'])
            
            return template
        except Exception as e:
            print(f"Error loading template config: {e}")
            return None


class BusinessPresentationBuilder:
    """
    High-level builder for creating business presentations with templates
    """
    
    def __init__(self):
        self.generator = EnhancedTemplateGenerator()
        self.current_presentation = None
    
    def start_presentation(self, title: str, theme: BusinessTheme = BusinessTheme.CORPORATE_BLUE) -> 'BusinessPresentationBuilder':
        """Start building a new presentation"""
        self.current_presentation = (BusinessDSLBuilder()
                                   .set_metadata(title=title)
                                   .set_theme(theme))
        return self
    
    def set_company_info(self, company: str, author: str, logo_path: str = None) -> 'BusinessPresentationBuilder':
        """Set company information"""
        if self.current_presentation:
            self.current_presentation.presentation.company = company
            self.current_presentation.presentation.author = author
            if logo_path:
                self.current_presentation.set_branding(logo_path=logo_path)
        return self
    
    def add_executive_summary_section(self, summary_points: List[str]) -> 'BusinessPresentationBuilder':
        """Add an executive summary section"""
        if self.current_presentation:
            self.current_presentation.add_section_divider("exec_summary", "Executive Summary")
            self.current_presentation.add_content_slide(
                "summary_content",
                "Key Highlights",
                "bullet_list",
                {"items": summary_points}
            )
        return self
    
    def add_financial_section(self, financial_data: Dict[str, Any]) -> 'BusinessPresentationBuilder':
        """Add a financial performance section"""
        if self.current_presentation:
            self.current_presentation.add_section_divider("financial", "Financial Performance")
            
            # Revenue slide
            if 'revenue' in financial_data:
                self.current_presentation.add_content_slide(
                    "revenue_chart",
                    "Revenue Performance",
                    "chart",
                    financial_data['revenue'],
                    SlideLayout.CHART_FOCUS
                )
            
            # Key metrics slide
            if 'metrics' in financial_data:
                self.current_presentation.add_content_slide(
                    "key_metrics",
                    "Key Financial Metrics",
                    "bullet_list",
                    {"items": financial_data['metrics']}
                )
        return self
    
    def add_market_analysis_section(self, market_data: Dict[str, Any]) -> 'BusinessPresentationBuilder':
        """Add market analysis section"""
        if self.current_presentation:
            self.current_presentation.add_section_divider("market", "Market Analysis")
            
            # Market overview
            if 'overview' in market_data:
                self.current_presentation.add_content_slide(
                    "market_overview",
                    "Market Overview",
                    "text",
                    {"text": market_data['overview']}
                )
            
            # Competitive landscape
            if 'competition' in market_data:
                self.current_presentation.add_content_slide(
                    "competition",
                    "Competitive Landscape",
                    "bullet_list",
                    {"items": market_data['competition']}
                )
        return self
    
    def add_strategy_section(self, strategy_data: Dict[str, Any]) -> 'BusinessPresentationBuilder':
        """Add strategic initiatives section"""
        if self.current_presentation:
            self.current_presentation.add_section_divider("strategy", "Strategic Initiatives")
            
            # Strategic priorities
            if 'priorities' in strategy_data:
                self.current_presentation.add_content_slide(
                    "strategic_priorities",
                    "Strategic Priorities",
                    "bullet_list",
                    {"items": strategy_data['priorities']}
                )
            
            # Implementation roadmap
            if 'roadmap' in strategy_data:
                self.current_presentation.add_content_slide(
                    "roadmap",
                    "Implementation Roadmap",
                    "bullet_list",
                    {"items": strategy_data['roadmap']}
                )
        return self
    
    def finalize(self, output_path: str = None) -> str:
        """Finalize and generate the presentation"""
        if not self.current_presentation:
            raise ValueError("No presentation started")
        
        # Add title and thank you slides
        presentation = (self.current_presentation
                       .add_title_slide()
                       .add_thank_you_slide()
                       .build())
        
        # Generate the presentation
        if not output_path:
            output_path = f"{presentation.title.replace(' ', '_').lower()}.pptx"
        
        return self.generator.create_presentation_from_dsl(presentation)


def create_sample_business_presentations():
    """Create sample business presentations using the new system"""
    
    # Example 1: Executive Summary Presentation
    exec_presentation = (BusinessPresentationBuilder()
                        .start_presentation("Q4 2023 Executive Summary", BusinessTheme.EXECUTIVE_DARK)
                        .set_company_info("Acme Corporation", "Jane Smith", "assets/acme_logo.png")
                        .add_executive_summary_section([
                            "Revenue increased 15% year-over-year",
                            "Successfully launched 3 new product lines",
                            "Expanded into 2 new international markets",
                            "Achieved 95% customer satisfaction rating"
                        ])
                        .add_financial_section({
                            'revenue': {
                                'chart_type': 'line',
                                'data': [100, 105, 110, 115],
                                'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                                'title': 'Quarterly Revenue Growth (in millions)'
                            },
                            'metrics': [
                                "Gross Margin: 42%",
                                "EBITDA: $25M",
                                "Cash Flow: $18M",
                                "ROI: 23%"
                            ]
                        })
                        .add_strategy_section({
                            'priorities': [
                                "Digital transformation initiative",
                                "Sustainable product development",
                                "Market expansion in Asia-Pacific",
                                "Talent acquisition and retention"
                            ],
                            'roadmap': [
                                "Q1: Complete digital platform migration",
                                "Q2: Launch sustainability program",
                                "Q3: Open Singapore office",
                                "Q4: Implement new HR systems"
                            ]
                        })
                        .finalize("executive_summary_q4_2023.pptx"))
    
    # Example 2: Sales Pitch Presentation
    sales_presentation = (BusinessPresentationBuilder()
                         .start_presentation("Product Launch Pitch", BusinessTheme.STARTUP_VIBRANT)
                         .set_company_info("TechStart Inc.", "Mike Johnson")
                         .add_executive_summary_section([
                             "Revolutionary AI-powered solution",
                             "Addresses $50B market opportunity",
                             "Proven traction with early customers",
                             "Seeking $5M Series A funding"
                         ])
                         .add_market_analysis_section({
                             'overview': "The enterprise software market is experiencing rapid growth, with AI adoption accelerating across all industries. Our solution addresses critical pain points in workflow automation.",
                             'competition': [
                                 "Legacy solutions lack AI capabilities",
                                 "Current alternatives are too complex",
                                 "No integrated solution exists",
                                 "Our approach is 10x faster"
                             ]
                         })
                         .finalize("product_launch_pitch.pptx"))
    
    return [exec_presentation, sales_presentation]


def demonstrate_template_customization():
    """Demonstrate how to create and customize templates"""
    
    generator = EnhancedTemplateGenerator()
    
    # Create a custom template for financial reports
    custom_header = HeaderConfig(
        show_logo=True,
        show_date=True,
        show_slide_number=True,
        alignment="left"
    )
    
    custom_footer = FooterConfig(
        show_company_name=True,
        show_confidentiality=True,
        confidentiality_text="Financial Data - Confidential",
        show_page_number=True,
        alignment="center"
    )
    
    custom_content = ContentConfig(
        padding=0.3,
        spacing=0.15,
        bullet_style="bullet",
        chart_style="financial"
    )
    
    # Create the custom template
    custom_template = generator.create_custom_template(
        "custom_financial",
        BusinessTheme.FINANCIAL_PROFESSIONAL,
        custom_header,
        custom_footer,
        custom_content
    )
    
    # Export the template configuration
    generator.export_template_config("custom_financial", "custom_financial_template.json")
    
    print("Custom template created and exported!")
    
    return custom_template


def create_component_layout_example():
    """Demonstrate creating custom component layouts"""
    
    # Create a custom layout for dashboard-style presentations
    layout = ComponentLayout()
    layout.layout_name = "dashboard"
    
    # Header with company branding
    header = HeaderComponent(
        bounds=ComponentBounds(0, 0, 10, 1.2),
        style=ComponentStyle(
            font_size=20,
            font_bold=True,
            background_color="#1f4e79",
            font_color="#ffffff"
        )
    )
    layout.add_component(header)
    
    # Main KPI section (left side)
    kpi_content = ContentComponent(
        component_id="kpi_section",
        bounds=ComponentBounds(0.5, 1.5, 4.5, 2.5),
        style=ComponentStyle(font_size=16, font_bold=True)
    )
    layout.add_component(kpi_content)
    
    # Chart section (right side)
    chart_content = ContentComponent(
        component_id="chart_section",
        bounds=ComponentBounds(5.25, 1.5, 4.25, 2.5),
        style=ComponentStyle(font_size=14)
    )
    layout.add_component(chart_content)
    
    # Bottom insights section (full width)
    insights_content = ContentComponent(
        component_id="insights_section",
        bounds=ComponentBounds(0.5, 4.25, 9, 1.75),
        style=ComponentStyle(font_size=12)
    )
    layout.add_component(insights_content)
    
    # Footer
    footer = FooterComponent(
        bounds=ComponentBounds(0, 6.5, 10, 0.5),
        style=ComponentStyle(font_size=10, alignment="center")
    )
    layout.add_component(footer)
    
    # Export the layout
    layout.export_layout("dashboard_layout.json")
    
    print("Custom dashboard layout created and exported!")
    
    return layout


# Usage examples and demonstrations
if __name__ == "__main__":
    print("=== PowerPoint Template System Integration Examples ===\n")
    
    # 1. Create sample business presentations
    print("1. Creating sample business presentations...")
    presentations = create_sample_business_presentations()
    print(f"Created {len(presentations)} sample presentations\n")
    
    # 2. Demonstrate template customization
    print("2. Demonstrating template customization...")
    custom_template = demonstrate_template_customization()
    print("Custom template demonstration complete\n")
    
    # 3. Create custom component layout
    print("3. Creating custom component layout...")
    dashboard_layout = create_component_layout_example()
    print("Custom layout demonstration complete\n")
    
    # 4. Show DSL usage
    print("4. Demonstrating DSL usage...")
    dsl_presentation = (BusinessDSLBuilder()
                       .set_metadata(
                           title="Integration Demo",
                           subtitle="Template System Showcase",
                           author="System Demo",
                           company="Demo Corp"
                       )
                       .set_theme(BusinessTheme.MODERN_MINIMAL)
                       .add_title_slide()
                       .add_content_slide(
                           "demo_content",
                           "Template Features",
                           "bullet_list",
                           {
                               "items": [
                                   "Modular component system",
                                   "Business-focused templates",
                                   "Flexible DSL structure",
                                   "Easy integration with existing code"
                               ]
                           }
                       )
                       .build())
    
    print("DSL demonstration complete")
    print(f"Generated presentation with {len(dsl_presentation.slides)} slides\n")
    
    print("=== Integration Examples Complete ===")