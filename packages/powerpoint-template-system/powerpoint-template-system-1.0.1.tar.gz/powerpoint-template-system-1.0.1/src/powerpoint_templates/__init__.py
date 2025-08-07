"""
PowerPoint Template System

A comprehensive template system for creating professional business presentations
with modern styling, cards, badges, and domain-specific language support.

Features:
- Modern card-based layouts with badges and gradients
- Professional business templates
- Domain-specific language (DSL) for presentations
- Enhanced visual generator with modern styling
- JSON-based configuration system
- XSD schema validation
"""

__version__ = "1.0.1"
__author__ = "PowerPoint Template System Team"
__email__ = "templates@cpro.com"

# Core imports
from .enhanced_business_dsl import (
    BusinessDSLBuilder,
    BusinessPresentationDSL,
    SlideHeader,
    SlideFooter,
    SlideContent,
    BusinessTheme,
)

from .enhanced_visual_generator import (
    EnhancedVisualGenerator,
)

from .template_system_design import (
    BusinessPresentationTemplate,
    TemplateLibrary,
    StyleConfig,
    HeaderConfig,
    FooterConfig,
    ContentConfig,
)

from .modular_components import (
    PresentationComponent,
    HeaderComponent,
    FooterComponent,
    ContentComponent,
    ComponentLayout,
    ComponentBounds,
    ComponentStyle,
    ComponentType,
    ComponentPosition,
)

from .business_template_examples import (
    BusinessTemplateExamples,
    generate_all_sample_presentations,
)

from .integration_examples import (
    EnhancedTemplateGenerator,
    BusinessPresentationBuilder,
    create_sample_business_presentations,
    demonstrate_template_customization,
    create_component_layout_example,
)

# Version info
__all__ = [
    # Version
    "__version__",
    "__author__",
    "__email__",
    
    # Core DSL
    "BusinessDSLBuilder",
    "BusinessPresentationDSL",
    "SlideHeader",
    "SlideFooter",
    "SlideContent",
    "BusinessTheme",
    
    # Visual Generator
    "EnhancedVisualGenerator",
    
    # Template System
    "BusinessPresentationTemplate",
    "TemplateLibrary",
    "StyleConfig",
    "HeaderConfig",
    "FooterConfig",
    "ContentConfig",
    
    # Components
    "PresentationComponent",
    "HeaderComponent",
    "FooterComponent",
    "ContentComponent",
    "ComponentLayout",
    "ComponentBounds",
    "ComponentStyle",
    "ComponentType",
    "ComponentPosition",
    
    # Business Templates
    "BusinessTemplateExamples",
    "generate_all_sample_presentations",
    
    # Integration
    "EnhancedTemplateGenerator",
    "BusinessPresentationBuilder",
    "create_sample_business_presentations",
    "demonstrate_template_customization",
    "create_component_layout_example",
]