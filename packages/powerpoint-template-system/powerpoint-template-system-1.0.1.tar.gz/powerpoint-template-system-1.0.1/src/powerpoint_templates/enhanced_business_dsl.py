"""
Enhanced DSL Structure for Business PowerPoint Generation

This module provides an improved DSL that integrates with the template system
for easier business presentation creation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import xml.etree.ElementTree as ET
from .template_system_design import BusinessTheme, SlideLayout


@dataclass
class BusinessPresentationDSL:
    """Enhanced DSL for business presentations"""
    
    # Presentation metadata
    title: str
    subtitle: Optional[str] = None
    author: str = ""
    company: str = ""
    date: Optional[str] = None
    
    # Template and theme configuration
    theme: BusinessTheme = BusinessTheme.CORPORATE_BLUE
    template_name: str = "standard_business"
    
    # Global settings
    show_slide_numbers: bool = True
    show_company_footer: bool = True
    confidentiality_level: str = "Internal"
    
    # Slide definitions
    slides: List['BusinessSlide'] = field(default_factory=list)
    
    # Brand assets
    logo_path: Optional[str] = None
    brand_colors: Dict[str, str] = field(default_factory=dict)
    
    def to_xml(self) -> str:
        """Convert DSL to XML representation"""
        root = ET.Element("business_presentation")
        
        # Metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "title").text = self.title
        if self.subtitle:
            ET.SubElement(metadata, "subtitle").text = self.subtitle
        ET.SubElement(metadata, "author").text = self.author
        ET.SubElement(metadata, "company").text = self.company
        if self.date:
            ET.SubElement(metadata, "date").text = self.date
        
        # Configuration
        config = ET.SubElement(root, "configuration")
        ET.SubElement(config, "theme").text = self.theme.value
        ET.SubElement(config, "template").text = self.template_name
        ET.SubElement(config, "show_slide_numbers").text = str(self.show_slide_numbers)
        ET.SubElement(config, "show_company_footer").text = str(self.show_company_footer)
        ET.SubElement(config, "confidentiality_level").text = self.confidentiality_level
        
        # Brand assets
        if self.logo_path or self.brand_colors:
            brand = ET.SubElement(root, "brand_assets")
            if self.logo_path:
                ET.SubElement(brand, "logo_path").text = self.logo_path
            if self.brand_colors:
                colors = ET.SubElement(brand, "brand_colors")
                for color_name, color_value in self.brand_colors.items():
                    color_elem = ET.SubElement(colors, "color")
                    color_elem.set("name", color_name)
                    color_elem.text = color_value
        
        # Slides
        slides_elem = ET.SubElement(root, "slides")
        for slide in self.slides:
            slides_elem.append(slide.to_xml_element())
        
        return ET.tostring(root, encoding='unicode')
    
    @classmethod
    def from_xml(cls, xml_string: str) -> 'BusinessPresentationDSL':
        """Create DSL from XML representation"""
        root = ET.fromstring(xml_string)
        
        # Parse metadata
        metadata = root.find("metadata")
        title = metadata.find("title").text
        subtitle = metadata.find("subtitle").text if metadata.find("subtitle") is not None else None
        author = metadata.find("author").text or ""
        company = metadata.find("company").text or ""
        date = metadata.find("date").text if metadata.find("date") is not None else None
        
        # Parse configuration
        config = root.find("configuration")
        theme = BusinessTheme(config.find("theme").text)
        template_name = config.find("template").text
        show_slide_numbers = config.find("show_slide_numbers").text.lower() == "true"
        show_company_footer = config.find("show_company_footer").text.lower() == "true"
        confidentiality_level = config.find("confidentiality_level").text
        
        # Parse brand assets
        logo_path = None
        brand_colors = {}
        brand_assets = root.find("brand_assets")
        if brand_assets is not None:
            logo_elem = brand_assets.find("logo_path")
            if logo_elem is not None:
                logo_path = logo_elem.text
            
            colors_elem = brand_assets.find("brand_colors")
            if colors_elem is not None:
                for color_elem in colors_elem.findall("color"):
                    brand_colors[color_elem.get("name")] = color_elem.text
        
        # Parse slides
        slides = []
        slides_elem = root.find("slides")
        if slides_elem is not None:
            for slide_elem in slides_elem.findall("slide"):
                slides.append(BusinessSlide.from_xml_element(slide_elem))
        
        return cls(
            title=title,
            subtitle=subtitle,
            author=author,
            company=company,
            date=date,
            theme=theme,
            template_name=template_name,
            show_slide_numbers=show_slide_numbers,
            show_company_footer=show_company_footer,
            confidentiality_level=confidentiality_level,
            slides=slides,
            logo_path=logo_path,
            brand_colors=brand_colors
        )


@dataclass
class BusinessSlide:
    """Enhanced slide definition for business presentations"""
    
    # Slide identification
    slide_id: str
    slide_type: str  # Maps to template types like 'title', 'content', 'section', etc.
    
    # Layout configuration
    layout: SlideLayout = SlideLayout.FULL_CONTENT
    
    # Content sections
    header: Optional['SlideHeader'] = None
    content: 'SlideContent' = None
    footer: Optional['SlideFooter'] = None
    
    # Slide-specific overrides
    hide_header: bool = False
    hide_footer: bool = False
    custom_background: Optional[str] = None
    
    # Animation and transition settings
    transition: Optional[str] = None
    animations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_xml_element(self) -> ET.Element:
        """Convert slide to XML element"""
        slide_elem = ET.Element("slide")
        slide_elem.set("id", self.slide_id)
        slide_elem.set("type", self.slide_type)
        slide_elem.set("layout", self.layout.value)
        
        if self.hide_header:
            slide_elem.set("hide_header", "true")
        if self.hide_footer:
            slide_elem.set("hide_footer", "true")
        if self.custom_background:
            slide_elem.set("custom_background", self.custom_background)
        if self.transition:
            slide_elem.set("transition", self.transition)
        
        # Add header
        if self.header:
            slide_elem.append(self.header.to_xml_element())
        
        # Add content
        if self.content:
            slide_elem.append(self.content.to_xml_element())
        
        # Add footer
        if self.footer:
            slide_elem.append(self.footer.to_xml_element())
        
        # Add animations
        if self.animations:
            animations_elem = ET.SubElement(slide_elem, "animations")
            for animation in self.animations:
                anim_elem = ET.SubElement(animations_elem, "animation")
                for key, value in animation.items():
                    anim_elem.set(key, str(value))
        
        return slide_elem
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'BusinessSlide':
        """Create slide from XML element"""
        slide_id = element.get("id")
        slide_type = element.get("type")
        layout = SlideLayout(element.get("layout", SlideLayout.FULL_CONTENT.value))
        
        hide_header = element.get("hide_header", "false").lower() == "true"
        hide_footer = element.get("hide_footer", "false").lower() == "true"
        custom_background = element.get("custom_background")
        transition = element.get("transition")
        
        # Parse header
        header = None
        header_elem = element.find("header")
        if header_elem is not None:
            header = SlideHeader.from_xml_element(header_elem)
        
        # Parse content
        content = None
        content_elem = element.find("content")
        if content_elem is not None:
            content = SlideContent.from_xml_element(content_elem)
        
        # Parse footer
        footer = None
        footer_elem = element.find("footer")
        if footer_elem is not None:
            footer = SlideFooter.from_xml_element(footer_elem)
        
        # Parse animations
        animations = []
        animations_elem = element.find("animations")
        if animations_elem is not None:
            for anim_elem in animations_elem.findall("animation"):
                animation = dict(anim_elem.attrib)
                animations.append(animation)
        
        return cls(
            slide_id=slide_id,
            slide_type=slide_type,
            layout=layout,
            header=header,
            content=content,
            footer=footer,
            hide_header=hide_header,
            hide_footer=hide_footer,
            custom_background=custom_background,
            transition=transition,
            animations=animations
        )


@dataclass
class SlideHeader:
    """Header configuration for individual slides"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    show_logo: bool = True
    show_date: bool = False
    custom_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML element"""
        header_elem = ET.Element("header")
        
        if self.title:
            ET.SubElement(header_elem, "title").text = self.title
        if self.subtitle:
            ET.SubElement(header_elem, "subtitle").text = self.subtitle
        
        header_elem.set("show_logo", str(self.show_logo))
        header_elem.set("show_date", str(self.show_date))
        
        if self.custom_elements:
            custom_elem = ET.SubElement(header_elem, "custom_elements")
            for i, element in enumerate(self.custom_elements):
                elem = ET.SubElement(custom_elem, "element")
                elem.set("index", str(i))
                for key, value in element.items():
                    elem.set(key, str(value))
        
        return header_elem
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'SlideHeader':
        """Create from XML element"""
        title = element.find("title").text if element.find("title") is not None else None
        subtitle = element.find("subtitle").text if element.find("subtitle") is not None else None
        show_logo = element.get("show_logo", "true").lower() == "true"
        show_date = element.get("show_date", "false").lower() == "true"
        
        custom_elements = []
        custom_elem = element.find("custom_elements")
        if custom_elem is not None:
            for elem in custom_elem.findall("element"):
                custom_elements.append(dict(elem.attrib))
        
        return cls(
            title=title,
            subtitle=subtitle,
            show_logo=show_logo,
            show_date=show_date,
            custom_elements=custom_elements
        )


@dataclass
class SlideContent:
    """Content configuration for slides"""
    content_type: str  # text, chart, image, table, mixed, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML element"""
        content_elem = ET.Element("content")
        content_elem.set("type", self.content_type)
        
        # Add data elements
        for key, value in self.data.items():
            if isinstance(value, (str, int, float, bool)):
                elem = ET.SubElement(content_elem, key)
                elem.text = str(value)
            elif isinstance(value, list):
                list_elem = ET.SubElement(content_elem, key)
                for i, item in enumerate(value):
                    item_elem = ET.SubElement(list_elem, "item")
                    item_elem.set("index", str(i))
                    if isinstance(item, dict):
                        for k, v in item.items():
                            item_elem.set(k, str(v))
                    else:
                        item_elem.text = str(item)
            elif isinstance(value, dict):
                dict_elem = ET.SubElement(content_elem, key)
                for k, v in value.items():
                    sub_elem = ET.SubElement(dict_elem, k)
                    sub_elem.text = str(v)
        
        return content_elem
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'SlideContent':
        """Create from XML element"""
        content_type = element.get("type")
        data = {}
        
        for child in element:
            if child.tag == "item":
                continue  # Handle lists separately
            
            # Handle simple elements
            if len(child) == 0:
                data[child.tag] = child.text
            else:
                # Handle complex elements (lists, dicts)
                if child.find("item") is not None:
                    # It's a list
                    items = []
                    for item in child.findall("item"):
                        if item.attrib:
                            items.append(dict(item.attrib))
                        else:
                            items.append(item.text)
                    data[child.tag] = items
                else:
                    # It's a dict
                    sub_data = {}
                    for sub_child in child:
                        sub_data[sub_child.tag] = sub_child.text
                    data[child.tag] = sub_data
        
        return cls(content_type=content_type, data=data)


@dataclass
class SlideFooter:
    """Footer configuration for individual slides"""
    show_page_number: bool = True
    show_company_name: bool = True
    show_confidentiality: bool = True
    custom_text: Optional[str] = None
    custom_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_xml_element(self) -> ET.Element:
        """Convert to XML element"""
        footer_elem = ET.Element("footer")
        footer_elem.set("show_page_number", str(self.show_page_number))
        footer_elem.set("show_company_name", str(self.show_company_name))
        footer_elem.set("show_confidentiality", str(self.show_confidentiality))
        
        if self.custom_text:
            ET.SubElement(footer_elem, "custom_text").text = self.custom_text
        
        if self.custom_elements:
            custom_elem = ET.SubElement(footer_elem, "custom_elements")
            for i, element in enumerate(self.custom_elements):
                elem = ET.SubElement(custom_elem, "element")
                elem.set("index", str(i))
                for key, value in element.items():
                    elem.set(key, str(value))
        
        return footer_elem
    
    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'SlideFooter':
        """Create from XML element"""
        show_page_number = element.get("show_page_number", "true").lower() == "true"
        show_company_name = element.get("show_company_name", "true").lower() == "true"
        show_confidentiality = element.get("show_confidentiality", "true").lower() == "true"
        
        custom_text = None
        custom_text_elem = element.find("custom_text")
        if custom_text_elem is not None:
            custom_text = custom_text_elem.text
        
        custom_elements = []
        custom_elem = element.find("custom_elements")
        if custom_elem is not None:
            for elem in custom_elem.findall("element"):
                custom_elements.append(dict(elem.attrib))
        
        return cls(
            show_page_number=show_page_number,
            show_company_name=show_company_name,
            show_confidentiality=show_confidentiality,
            custom_text=custom_text,
            custom_elements=custom_elements
        )


class BusinessDSLBuilder:
    """Builder class for creating business presentations using DSL"""
    
    def __init__(self):
        self.presentation = BusinessPresentationDSL(title="")
    
    def set_metadata(self, title: str, subtitle: str = None, author: str = "", 
                    company: str = "", date: str = None) -> 'BusinessDSLBuilder':
        """Set presentation metadata"""
        self.presentation.title = title
        self.presentation.subtitle = subtitle
        self.presentation.author = author
        self.presentation.company = company
        self.presentation.date = date
        return self
    
    def set_theme(self, theme: BusinessTheme, template_name: str = "standard_business") -> 'BusinessDSLBuilder':
        """Set presentation theme and template"""
        self.presentation.theme = theme
        self.presentation.template_name = template_name
        return self
    
    def set_branding(self, logo_path: str = None, brand_colors: Dict[str, str] = None) -> 'BusinessDSLBuilder':
        """Set branding elements"""
        if logo_path:
            self.presentation.logo_path = logo_path
        if brand_colors:
            self.presentation.brand_colors = brand_colors
        return self
    
    def add_title_slide(self, slide_id: str = "title") -> 'BusinessDSLBuilder':
        """Add a title slide"""
        slide = BusinessSlide(
            slide_id=slide_id,
            slide_type="title",
            layout=SlideLayout.TITLE_SLIDE,
            content=SlideContent(
                content_type="title",
                data={
                    "title": self.presentation.title,
                    "subtitle": self.presentation.subtitle or "",
                    "author": self.presentation.author,
                    "company": self.presentation.company,
                    "date": self.presentation.date or ""
                }
            ),
            hide_header=True
        )
        self.presentation.slides.append(slide)
        return self
    
    def add_agenda_slide(self, slide_id: str, agenda_items: List[str]) -> 'BusinessDSLBuilder':
        """Add an agenda slide"""
        slide = BusinessSlide(
            slide_id=slide_id,
            slide_type="agenda",
            layout=SlideLayout.AGENDA,
            header=SlideHeader(title="Agenda"),
            content=SlideContent(
                content_type="agenda",
                data={"items": agenda_items}
            )
        )
        self.presentation.slides.append(slide)
        return self
    
    def add_content_slide(self, slide_id: str, title: str, content_type: str, 
                         content_data: Dict[str, Any], layout: SlideLayout = SlideLayout.FULL_CONTENT) -> 'BusinessDSLBuilder':
        """Add a content slide"""
        slide = BusinessSlide(
            slide_id=slide_id,
            slide_type="content",
            layout=layout,
            header=SlideHeader(title=title),
            content=SlideContent(
                content_type=content_type,
                data=content_data
            )
        )
        self.presentation.slides.append(slide)
        return self
    
    def add_section_divider(self, slide_id: str, section_title: str, 
                           section_subtitle: str = None) -> 'BusinessDSLBuilder':
        """Add a section divider slide"""
        slide = BusinessSlide(
            slide_id=slide_id,
            slide_type="section",
            layout=SlideLayout.SECTION_DIVIDER,
            content=SlideContent(
                content_type="section_divider",
                data={
                    "title": section_title,
                    "subtitle": section_subtitle or ""
                }
            ),
            hide_header=True,
            hide_footer=True
        )
        self.presentation.slides.append(slide)
        return self
    
    def add_thank_you_slide(self, slide_id: str = "thank_you", 
                           contact_info: Dict[str, str] = None) -> 'BusinessDSLBuilder':
        """Add a thank you slide"""
        slide = BusinessSlide(
            slide_id=slide_id,
            slide_type="thank_you",
            layout=SlideLayout.THANK_YOU,
            content=SlideContent(
                content_type="thank_you",
                data={
                    "message": "Thank You",
                    "contact_info": contact_info or {}
                }
            ),
            hide_header=True
        )
        self.presentation.slides.append(slide)
        return self
    
    def build(self) -> BusinessPresentationDSL:
        """Build and return the presentation DSL"""
        return self.presentation


# Usage examples
if __name__ == "__main__":
    # Example 1: Using the builder pattern
    presentation = (BusinessDSLBuilder()
                   .set_metadata(
                       title="Q4 Business Review",
                       subtitle="Financial Performance & Strategic Outlook",
                       author="John Smith",
                       company="Acme Corporation",
                       date="2024-01-15"
                   )
                   .set_theme(BusinessTheme.CORPORATE_BLUE, "executive_summary")
                   .set_branding(
                       logo_path="assets/company_logo.png",
                       brand_colors={"primary": "#1f4e79", "secondary": "#70ad47"}
                   )
                   .add_title_slide()
                   .add_agenda_slide("agenda", [
                       "Executive Summary",
                       "Financial Performance",
                       "Market Analysis",
                       "Strategic Initiatives",
                       "Q1 Outlook"
                   ])
                   .add_section_divider("section1", "Financial Performance", "Q4 2023 Results")
                   .add_content_slide(
                       "revenue_chart",
                       "Revenue Growth",
                       "chart",
                       {
                           "chart_type": "line",
                           "data": [100, 120, 135, 150],
                           "labels": ["Q1", "Q2", "Q3", "Q4"],
                           "title": "Quarterly Revenue (in millions)"
                       },
                       SlideLayout.CHART_FOCUS
                   )
                   .add_thank_you_slide(contact_info={
                       "email": "john.smith@acme.com",
                       "phone": "+1-555-0123"
                   })
                   .build())
    
    # Export to XML
    xml_output = presentation.to_xml()
    print("Generated XML DSL:")
    print(xml_output[:500] + "..." if len(xml_output) > 500 else xml_output)