"""
High-Level Template Abstraction System for Business PowerPoint Generation

This module provides a comprehensive template system with:
1. Reusable header/content/footer components
2. Business-focused presentation templates
3. Theme and styling management
4. Configuration-driven approach
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
from pathlib import Path


class BusinessTheme(Enum):
    """Predefined business themes for presentations"""
    CORPORATE_BLUE = "corporate_blue"
    EXECUTIVE_DARK = "executive_dark"
    MODERN_MINIMAL = "modern_minimal"
    STARTUP_VIBRANT = "startup_vibrant"
    CONSULTING_CLEAN = "consulting_clean"
    FINANCIAL_PROFESSIONAL = "financial_professional"


class SlideLayout(Enum):
    """Enhanced slide layout types for business presentations"""
    TITLE_SLIDE = "title_slide"
    AGENDA = "agenda"
    SECTION_DIVIDER = "section_divider"
    CONTENT_WITH_SIDEBAR = "content_with_sidebar"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    FULL_CONTENT = "full_content"
    CHART_FOCUS = "chart_focus"
    IMAGE_FOCUS = "image_focus"
    QUOTE_TESTIMONIAL = "quote_testimonial"
    THANK_YOU = "thank_you"
    CONTACT_INFO = "contact_info"


@dataclass
class StyleConfig:
    """Configuration for styling elements"""
    font_family: str = "Calibri"
    primary_color: str = "#1f4e79"
    secondary_color: str = "#70ad47"
    accent_color: str = "#c55a11"
    background_color: str = "#ffffff"
    text_color: str = "#000000"
    header_height: float = 1.0  # inches
    footer_height: float = 0.5  # inches
    margin_left: float = 0.5
    margin_right: float = 0.5
    margin_top: float = 0.5
    margin_bottom: float = 0.5


@dataclass
class HeaderConfig:
    """Configuration for slide headers"""
    show_logo: bool = True
    logo_path: Optional[str] = None
    show_title: bool = True
    show_subtitle: bool = False
    show_date: bool = False
    show_slide_number: bool = True
    alignment: str = "left"  # left, center, right
    background_color: Optional[str] = None
    border_bottom: bool = True
    custom_elements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FooterConfig:
    """Configuration for slide footers"""
    show_company_name: bool = True
    company_name: str = ""
    show_confidentiality: bool = True
    confidentiality_text: str = "Confidential"
    show_page_number: bool = True
    show_date: bool = False
    alignment: str = "center"
    background_color: Optional[str] = None
    border_top: bool = True
    custom_elements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ContentConfig:
    """Configuration for slide content areas"""
    layout_type: SlideLayout = SlideLayout.FULL_CONTENT
    padding: float = 0.25
    spacing: float = 0.1
    bullet_style: str = "bullet"
    max_bullet_levels: int = 3
    chart_style: str = "modern"
    table_style: str = "medium"
    image_border: bool = False
    content_alignment: str = "left"


class ComponentTemplate(ABC):
    """Abstract base class for slide components"""
    
    def __init__(self, config: Union[HeaderConfig, FooterConfig, ContentConfig]):
        self.config = config
    
    @abstractmethod
    def render(self, slide, data: Dict[str, Any]) -> None:
        """Render the component on the slide"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate the data required for this component"""
        pass


class HeaderTemplate(ComponentTemplate):
    """Template for slide headers"""
    
    def __init__(self, config: HeaderConfig, style: StyleConfig):
        super().__init__(config)
        self.style = style
    
    def render(self, slide, data: Dict[str, Any]) -> None:
        """Render header component"""
        # Implementation would create header elements based on config
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate header data"""
        required_fields = []
        if self.config.show_title:
            required_fields.append('title')
        if self.config.show_subtitle:
            required_fields.append('subtitle')
        
        return all(field in data for field in required_fields)


class FooterTemplate(ComponentTemplate):
    """Template for slide footers"""
    
    def __init__(self, config: FooterConfig, style: StyleConfig):
        super().__init__(config)
        self.style = style
    
    def render(self, slide, data: Dict[str, Any]) -> None:
        """Render footer component"""
        # Implementation would create footer elements based on config
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate footer data"""
        return True  # Footer typically doesn't require external data


class ContentTemplate(ComponentTemplate):
    """Template for slide content"""
    
    def __init__(self, config: ContentConfig, style: StyleConfig):
        super().__init__(config)
        self.style = style
    
    def render(self, slide, data: Dict[str, Any]) -> None:
        """Render content component based on layout type"""
        layout_renderers = {
            SlideLayout.TITLE_SLIDE: self._render_title_slide,
            SlideLayout.AGENDA: self._render_agenda,
            SlideLayout.SECTION_DIVIDER: self._render_section_divider,
            SlideLayout.TWO_COLUMN: self._render_two_column,
            SlideLayout.THREE_COLUMN: self._render_three_column,
            SlideLayout.CHART_FOCUS: self._render_chart_focus,
            SlideLayout.IMAGE_FOCUS: self._render_image_focus,
            # Add more layout renderers
        }
        
        renderer = layout_renderers.get(self.config.layout_type)
        if renderer:
            renderer(slide, data)
    
    def _render_title_slide(self, slide, data: Dict[str, Any]) -> None:
        """Render title slide layout"""
        pass
    
    def _render_agenda(self, slide, data: Dict[str, Any]) -> None:
        """Render agenda layout"""
        pass
    
    def _render_section_divider(self, slide, data: Dict[str, Any]) -> None:
        """Render section divider layout"""
        pass
    
    def _render_two_column(self, slide, data: Dict[str, Any]) -> None:
        """Render two-column layout"""
        pass
    
    def _render_three_column(self, slide, data: Dict[str, Any]) -> None:
        """Render three-column layout"""
        pass
    
    def _render_chart_focus(self, slide, data: Dict[str, Any]) -> None:
        """Render chart-focused layout"""
        pass
    
    def _render_image_focus(self, slide, data: Dict[str, Any]) -> None:
        """Render image-focused layout"""
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate content data based on layout type"""
        # Implementation would validate based on layout requirements
        return True


@dataclass
class SlideTemplate:
    """Complete slide template combining header, content, and footer"""
    header: Optional[HeaderTemplate] = None
    content: ContentTemplate = None
    footer: Optional[FooterTemplate] = None
    style: StyleConfig = field(default_factory=StyleConfig)
    
    def render_slide(self, slide, data: Dict[str, Any]) -> None:
        """Render complete slide using all components"""
        if self.header:
            self.header.render(slide, data.get('header', {}))
        
        if self.content:
            self.content.render(slide, data.get('content', {}))
        
        if self.footer:
            self.footer.render(slide, data.get('footer', {}))
    
    def validate_slide_data(self, data: Dict[str, Any]) -> bool:
        """Validate all slide data"""
        validations = []
        
        if self.header:
            validations.append(self.header.validate_data(data.get('header', {})))
        
        if self.content:
            validations.append(self.content.validate_data(data.get('content', {})))
        
        if self.footer:
            validations.append(self.footer.validate_data(data.get('footer', {})))
        
        return all(validations)


class BusinessPresentationTemplate:
    """High-level business presentation template"""
    
    def __init__(self, theme: BusinessTheme, template_name: str):
        self.theme = theme
        self.template_name = template_name
        self.style = self._load_theme_style(theme)
        self.slide_templates: Dict[str, SlideTemplate] = {}
        self._initialize_templates()
    
    def _load_theme_style(self, theme: BusinessTheme) -> StyleConfig:
        """Load style configuration for the theme"""
        theme_configs = {
            BusinessTheme.CORPORATE_BLUE: StyleConfig(
                primary_color="#1f4e79",
                secondary_color="#70ad47",
                accent_color="#c55a11"
            ),
            BusinessTheme.EXECUTIVE_DARK: StyleConfig(
                primary_color="#2c3e50",
                secondary_color="#34495e",
                accent_color="#e74c3c",
                background_color="#ecf0f1"
            ),
            BusinessTheme.MODERN_MINIMAL: StyleConfig(
                primary_color="#2c3e50",
                secondary_color="#95a5a6",
                accent_color="#3498db",
                background_color="#ffffff"
            ),
            # Add more theme configurations
        }
        
        return theme_configs.get(theme, StyleConfig())
    
    def _initialize_templates(self) -> None:
        """Initialize slide templates for business presentations"""
        # Title slide template
        self.slide_templates['title'] = SlideTemplate(
            header=None,  # Title slides typically don't have headers
            content=ContentTemplate(
                ContentConfig(layout_type=SlideLayout.TITLE_SLIDE),
                self.style
            ),
            footer=FooterTemplate(
                FooterConfig(show_page_number=False),
                self.style
            ),
            style=self.style
        )
        
        # Standard content slide
        self.slide_templates['content'] = SlideTemplate(
            header=HeaderTemplate(
                HeaderConfig(show_logo=True, show_slide_number=True),
                self.style
            ),
            content=ContentTemplate(
                ContentConfig(layout_type=SlideLayout.FULL_CONTENT),
                self.style
            ),
            footer=FooterTemplate(FooterConfig(), self.style),
            style=self.style
        )
        
        # Section divider
        self.slide_templates['section'] = SlideTemplate(
            header=None,
            content=ContentTemplate(
                ContentConfig(layout_type=SlideLayout.SECTION_DIVIDER),
                self.style
            ),
            footer=FooterTemplate(
                FooterConfig(show_page_number=False),
                self.style
            ),
            style=self.style
        )
        
        # Add more template types as needed
    
    def get_slide_template(self, template_type: str) -> Optional[SlideTemplate]:
        """Get a specific slide template"""
        return self.slide_templates.get(template_type)
    
    def add_custom_template(self, name: str, template: SlideTemplate) -> None:
        """Add a custom slide template"""
        self.slide_templates[name] = template
    
    def export_config(self, file_path: str) -> None:
        """Export template configuration to JSON file"""
        config_data = {
            'theme': self.theme.value,
            'template_name': self.template_name,
            'style': self.style.__dict__,
            'templates': list(self.slide_templates.keys())
        }
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)


class TemplateLibrary:
    """Library of predefined business presentation templates"""
    
    @staticmethod
    def get_executive_summary_template() -> BusinessPresentationTemplate:
        """Template for executive summary presentations"""
        template = BusinessPresentationTemplate(
            BusinessTheme.EXECUTIVE_DARK,
            "Executive Summary"
        )
        
        # Customize for executive presentations
        template.slide_templates['executive_summary'] = SlideTemplate(
            header=HeaderTemplate(
                HeaderConfig(show_logo=True, show_date=True),
                template.style
            ),
            content=ContentTemplate(
                ContentConfig(layout_type=SlideLayout.CONTENT_WITH_SIDEBAR),
                template.style
            ),
            footer=FooterTemplate(
                FooterConfig(confidentiality_text="Executive Summary - Confidential"),
                template.style
            ),
            style=template.style
        )
        
        return template
    
    @staticmethod
    def get_sales_pitch_template() -> BusinessPresentationTemplate:
        """Template for sales pitch presentations"""
        template = BusinessPresentationTemplate(
            BusinessTheme.STARTUP_VIBRANT,
            "Sales Pitch"
        )
        
        # Add sales-specific templates
        template.slide_templates['value_proposition'] = SlideTemplate(
            content=ContentTemplate(
                ContentConfig(layout_type=SlideLayout.IMAGE_FOCUS),
                template.style
            ),
            footer=FooterTemplate(FooterConfig(), template.style),
            style=template.style
        )
        
        return template
    
    @staticmethod
    def get_financial_report_template() -> BusinessPresentationTemplate:
        """Template for financial report presentations"""
        template = BusinessPresentationTemplate(
            BusinessTheme.FINANCIAL_PROFESSIONAL,
            "Financial Report"
        )
        
        # Add financial-specific templates
        template.slide_templates['financial_chart'] = SlideTemplate(
            header=HeaderTemplate(
                HeaderConfig(show_logo=True, show_date=True),
                template.style
            ),
            content=ContentTemplate(
                ContentConfig(layout_type=SlideLayout.CHART_FOCUS),
                template.style
            ),
            footer=FooterTemplate(
                FooterConfig(confidentiality_text="Financial Data - Confidential"),
                template.style
            ),
            style=template.style
        )
        
        return template


# Usage example
if __name__ == "__main__":
    # Create a business presentation template
    template = TemplateLibrary.get_executive_summary_template()
    
    # Export configuration
    template.export_config("executive_template_config.json")
    
    # Get specific slide template
    title_template = template.get_slide_template('title')
    
    print(f"Created {template.template_name} template with {len(template.slide_templates)} slide types")