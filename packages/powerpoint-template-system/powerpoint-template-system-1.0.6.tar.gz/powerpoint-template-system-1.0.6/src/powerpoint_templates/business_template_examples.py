"""
Sample Business Presentation Templates

This module provides ready-to-use business presentation templates for common scenarios.
"""

from .enhanced_business_dsl import BusinessDSLBuilder, BusinessTheme, SlideLayout
from .template_system_design import TemplateLibrary
from typing import Dict, List, Any


class BusinessTemplateExamples:
    """Collection of business presentation template examples"""
    
    @staticmethod
    def create_quarterly_business_review():
        """Create a comprehensive quarterly business review presentation"""
        return (BusinessDSLBuilder()
                .set_metadata(
                    title="Q4 2023 Business Review",
                    subtitle="Performance Analysis & Strategic Outlook",
                    author="Executive Team",
                    company="Acme Corporation",
                    date="January 15, 2024"
                )
                .set_theme(BusinessTheme.CORPORATE_BLUE, "executive_summary")
                .set_branding(
                    logo_path="assets/company_logo.png",
                    brand_colors={
                        "primary": "#1f4e79",
                        "secondary": "#70ad47",
                        "accent": "#c55a11"
                    }
                )
                .add_title_slide()
                .add_agenda_slide("agenda", [
                    "Executive Summary",
                    "Financial Performance",
                    "Operational Highlights",
                    "Market Position",
                    "Strategic Initiatives",
                    "Q1 2024 Outlook",
                    "Questions & Discussion"
                ])
                .add_section_divider("exec_section", "Executive Summary", "Key Performance Highlights")
                .add_content_slide(
                    "exec_summary",
                    "Q4 2023 Key Achievements",
                    "bullet_list",
                    {
                        "items": [
                            "Revenue exceeded targets by 12% ($125M vs $112M target)",
                            "Successfully launched 3 new product lines",
                            "Expanded customer base by 28% (2,400 new customers)",
                            "Achieved 94% customer satisfaction rating",
                            "Completed acquisition of TechStart Inc.",
                            "Opened new facilities in Austin and Denver"
                        ]
                    }
                )
                .add_section_divider("financial_section", "Financial Performance", "Q4 2023 Results")
                .add_content_slide(
                    "revenue_chart",
                    "Revenue Growth Trajectory",
                    "chart",
                    {
                        "chart_type": "line",
                        "data": [95, 108, 118, 125],
                        "labels": ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023"],
                        "title": "Quarterly Revenue (in millions)",
                        "trend": "positive",
                        "growth_rate": "15% YoY"
                    },
                    SlideLayout.CHART_FOCUS
                )
                .add_content_slide(
                    "financial_metrics",
                    "Key Financial Metrics",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Revenue: $125M (↑15% YoY)", "level": 0},
                            {"text": "Gross Margin: 42.3% (↑2.1pp)", "level": 0},
                            {"text": "EBITDA: $28.5M (↑22% YoY)", "level": 0},
                            {"text": "Net Income: $18.2M (↑18% YoY)", "level": 0},
                            {"text": "Cash Flow from Operations: $22.1M", "level": 0},
                            {"text": "Return on Equity: 24.7%", "level": 0}
                        ]
                    }
                )
                .add_section_divider("operations_section", "Operational Highlights", "Performance & Efficiency")
                .add_content_slide(
                    "operational_metrics",
                    "Operational Excellence",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Production & Delivery", "level": 0},
                            {"text": "On-time delivery: 96.2% (↑3.1pp)", "level": 1},
                            {"text": "Manufacturing efficiency: 89.4%", "level": 1},
                            {"text": "Quality defect rate: 0.12% (↓0.08pp)", "level": 1},
                            {"text": "Customer Experience", "level": 0},
                            {"text": "Net Promoter Score: 67 (↑8 points)", "level": 1},
                            {"text": "Customer retention: 92.1%", "level": 1},
                            {"text": "Average response time: 2.3 hours", "level": 1}
                        ]
                    }
                )
                .add_section_divider("strategy_section", "Strategic Initiatives", "2024 Focus Areas")
                .add_content_slide(
                    "strategic_priorities",
                    "Strategic Priorities for 2024",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Digital Transformation", "level": 0},
                            {"text": "Complete ERP system migration by Q2", "level": 1},
                            {"text": "Launch customer self-service portal", "level": 1},
                            {"text": "Market Expansion", "level": 0},
                            {"text": "Enter European market (UK, Germany)", "level": 1},
                            {"text": "Establish partnerships in Asia-Pacific", "level": 1},
                            {"text": "Innovation & R&D", "level": 0},
                            {"text": "Increase R&D investment by 25%", "level": 1},
                            {"text": "Launch AI-powered product line", "level": 1}
                        ]
                    }
                )
                .add_section_divider("outlook_section", "Q1 2024 Outlook", "Projections & Goals")
                .add_content_slide(
                    "q1_outlook",
                    "Q1 2024 Targets & Expectations",
                    "bullet_list",
                    {
                        "items": [
                            "Revenue target: $132M (5.6% growth)",
                            "Launch 2 new product variants",
                            "Complete TechStart integration",
                            "Hire 45 new employees across all divisions",
                            "Achieve ISO 27001 certification",
                            "Begin European market entry preparations"
                        ]
                    }
                )
                .add_thank_you_slide(
                    contact_info={
                        "email": "executive.team@acme.com",
                        "phone": "+1-555-ACME-BIZ",
                        "website": "www.acme.com"
                    }
                )
                .build())
    
    @staticmethod
    def create_sales_pitch_presentation():
        """Create a compelling sales pitch presentation"""
        return (BusinessDSLBuilder()
                .set_metadata(
                    title="CloudSync Pro",
                    subtitle="Next-Generation Enterprise Cloud Integration Platform",
                    author="Sales Team",
                    company="CloudTech Solutions",
                    date="February 2024"
                )
                .set_theme(BusinessTheme.STARTUP_VIBRANT, "sales_pitch")
                .add_title_slide()
                .add_agenda_slide("agenda", [
                    "The Challenge",
                    "Our Solution",
                    "Key Benefits",
                    "Success Stories",
                    "Pricing & Packages",
                    "Next Steps"
                ])
                .add_section_divider("problem_section", "The Challenge", "What keeps CTOs awake at night?")
                .add_content_slide(
                    "market_problem",
                    "Enterprise Integration Challenges",
                    "bullet_list",
                    {
                        "items": [
                            "73% of enterprises use 10+ cloud services",
                            "Average integration project takes 8-12 months",
                            "Data silos cost companies $15M annually",
                            "Security breaches from poor integration: 67% increase",
                            "IT teams spend 60% of time on integration maintenance"
                        ]
                    }
                )
                .add_section_divider("solution_section", "Our Solution", "CloudSync Pro Platform")
                .add_content_slide(
                    "solution_overview",
                    "CloudSync Pro: Unified Integration Platform",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "One Platform, All Integrations", "level": 0},
                            {"text": "Connect 500+ enterprise applications", "level": 1},
                            {"text": "Pre-built connectors for major platforms", "level": 1},
                            {"text": "No-Code/Low-Code Integration", "level": 0},
                            {"text": "Visual workflow designer", "level": 1},
                            {"text": "Drag-and-drop interface", "level": 1},
                            {"text": "Enterprise-Grade Security", "level": 0},
                            {"text": "SOC 2 Type II certified", "level": 1},
                            {"text": "End-to-end encryption", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "key_benefits",
                    "Transform Your Integration Strategy",
                    "bullet_list",
                    {
                        "items": [
                            "⚡ 10x Faster Implementation: Days instead of months",
                            "💰 75% Cost Reduction: Lower TCO than traditional solutions",
                            "🔒 Enhanced Security: Zero-trust architecture",
                            "📈 Real-time Analytics: Complete visibility into data flows",
                            "🚀 Scalable Architecture: Handles enterprise-scale workloads",
                            "🛠️ Expert Support: 24/7 technical assistance"
                        ]
                    }
                )
                .add_section_divider("success_section", "Success Stories", "Customer Results")
                .add_content_slide(
                    "case_study_1",
                    "Fortune 500 Manufacturing Company",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Challenge:", "level": 0},
                            {"text": "Integrate 15 legacy systems with new ERP", "level": 1},
                            {"text": "Solution:", "level": 0},
                            {"text": "CloudSync Pro with custom connectors", "level": 1},
                            {"text": "Results:", "level": 0},
                            {"text": "Project completed in 6 weeks (vs 8 months)", "level": 1},
                            {"text": "Saved $2.3M in integration costs", "level": 1},
                            {"text": "Improved data accuracy by 94%", "level": 1}
                        ]
                    }
                )
                .add_section_divider("pricing_section", "Investment Options", "Flexible Pricing for Every Business")
                .add_content_slide(
                    "pricing_tiers",
                    "Choose Your CloudSync Pro Package",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Starter Package - $2,500/month", "level": 0},
                            {"text": "Up to 10 integrations", "level": 1},
                            {"text": "Basic support", "level": 1},
                            {"text": "Professional Package - $7,500/month", "level": 0},
                            {"text": "Unlimited integrations", "level": 1},
                            {"text": "Priority support + training", "level": 1},
                            {"text": "Enterprise Package - Custom pricing", "level": 0},
                            {"text": "White-label options", "level": 1},
                            {"text": "Dedicated success manager", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "next_steps",
                    "Ready to Transform Your Integration Strategy?",
                    "bullet_list",
                    {
                        "items": [
                            "🎯 Schedule a personalized demo",
                            "🔍 Free integration assessment",
                            "📊 ROI analysis for your specific use case",
                            "🚀 30-day pilot program available",
                            "💬 Speak with our integration experts"
                        ]
                    }
                )
                .add_thank_you_slide(
                    contact_info={
                        "email": "sales@cloudtech.com",
                        "phone": "+1-800-CLOUD-PRO",
                        "demo": "www.cloudtech.com/demo"
                    }
                )
                .build())
    
    @staticmethod
    def create_investor_pitch_deck():
        """Create an investor pitch deck presentation"""
        return (BusinessDSLBuilder()
                .set_metadata(
                    title="EcoTech Innovations",
                    subtitle="Series A Funding Presentation",
                    author="Founding Team",
                    company="EcoTech Innovations",
                    date="March 2024"
                )
                .set_theme(BusinessTheme.MODERN_MINIMAL, "investor_pitch")
                .add_title_slide()
                .add_agenda_slide("agenda", [
                    "Problem & Opportunity",
                    "Solution",
                    "Market Size",
                    "Business Model",
                    "Traction",
                    "Competition",
                    "Team",
                    "Financials",
                    "Funding Ask",
                    "Use of Funds"
                ])
                .add_section_divider("problem_section", "The Problem", "Climate Crisis Meets Technology Gap")
                .add_content_slide(
                    "problem_statement",
                    "The $2.5 Trillion Climate Challenge",
                    "bullet_list",
                    {
                        "items": [
                            "Industrial emissions account for 21% of global CO2",
                            "Current monitoring systems are 20+ years old",
                            "Companies lack real-time emission insights",
                            "Regulatory compliance costs increasing 15% annually",
                            "ESG reporting requirements becoming mandatory"
                        ]
                    }
                )
                .add_section_divider("solution_section", "Our Solution", "AI-Powered Emission Intelligence")
                .add_content_slide(
                    "solution_overview",
                    "EcoTech Platform: Smart Emission Management",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Real-time Monitoring", "level": 0},
                            {"text": "IoT sensors + AI analytics", "level": 1},
                            {"text": "99.7% accuracy in emission detection", "level": 1},
                            {"text": "Predictive Analytics", "level": 0},
                            {"text": "Forecast emission patterns", "level": 1},
                            {"text": "Optimize operations for sustainability", "level": 1},
                            {"text": "Automated Compliance", "level": 0},
                            {"text": "Generate regulatory reports", "level": 1},
                            {"text": "Ensure 100% compliance", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "market_size",
                    "Massive Market Opportunity",
                    "bullet_list",
                    {
                        "items": [
                            "Total Addressable Market: $127B by 2030",
                            "Serviceable Addressable Market: $23B",
                            "Serviceable Obtainable Market: $2.1B",
                            "Growing at 22% CAGR",
                            "Early market with few established players"
                        ]
                    }
                )
                .add_content_slide(
                    "business_model",
                    "Scalable SaaS Business Model",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Revenue Streams", "level": 0},
                            {"text": "SaaS subscriptions: $50K-500K annually", "level": 1},
                            {"text": "Professional services: 20% of ARR", "level": 1},
                            {"text": "Hardware partnerships: 15% commission", "level": 1},
                            {"text": "Unit Economics", "level": 0},
                            {"text": "Customer Acquisition Cost: $12K", "level": 1},
                            {"text": "Lifetime Value: $180K", "level": 1},
                            {"text": "LTV/CAC Ratio: 15:1", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "traction",
                    "Strong Early Traction",
                    "bullet_list",
                    {
                        "items": [
                            "12 enterprise customers signed",
                            "$1.2M ARR with 150% net revenue retention",
                            "Partnerships with 3 major industrial IoT providers",
                            "Patents filed for core AI algorithms",
                            "Team of 18 engineers and domain experts"
                        ]
                    }
                )
                .add_content_slide(
                    "funding_ask",
                    "Series A: $8M to Scale Operations",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Use of Funds", "level": 0},
                            {"text": "Product Development: 40% ($3.2M)", "level": 1},
                            {"text": "Sales & Marketing: 35% ($2.8M)", "level": 1},
                            {"text": "Team Expansion: 20% ($1.6M)", "level": 1},
                            {"text": "Operations & Infrastructure: 5% ($0.4M)", "level": 1},
                            {"text": "18-Month Milestones", "level": 0},
                            {"text": "Reach $5M ARR", "level": 1},
                            {"text": "50+ enterprise customers", "level": 1},
                            {"text": "Expand to European market", "level": 1}
                        ]
                    }
                )
                .add_thank_you_slide(
                    contact_info={
                        "email": "founders@ecotech.com",
                        "phone": "+1-555-ECO-TECH",
                        "website": "www.ecotech-innovations.com"
                    }
                )
                .build())
    
    @staticmethod
    def create_project_status_report():
        """Create a project status report presentation"""
        return (BusinessDSLBuilder()
                .set_metadata(
                    title="Digital Transformation Project",
                    subtitle="Monthly Status Report - February 2024",
                    author="Project Management Office",
                    company="Global Manufacturing Corp",
                    date="March 1, 2024"
                )
                .set_theme(BusinessTheme.CONSULTING_CLEAN, "project_status")
                .add_title_slide()
                .add_agenda_slide("agenda", [
                    "Executive Summary",
                    "Project Timeline",
                    "Key Accomplishments",
                    "Current Challenges",
                    "Risk Assessment",
                    "Budget Status",
                    "Next Month Priorities",
                    "Resource Requirements"
                ])
                .add_content_slide(
                    "exec_summary",
                    "Project Health: On Track",
                    "bullet_list",
                    {
                        "items": [
                            "✅ Overall Status: GREEN - On schedule and budget",
                            "📊 Progress: 67% complete (vs 65% planned)",
                            "💰 Budget: $2.1M spent of $3.2M total (66% utilized)",
                            "👥 Team: 23 resources across 4 workstreams",
                            "🎯 Next Milestone: User Acceptance Testing (March 15)",
                            "⚠️ Key Risk: Integration testing delays"
                        ]
                    }
                )
                .add_content_slide(
                    "accomplishments",
                    "February 2024 Key Accomplishments",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Technical Achievements", "level": 0},
                            {"text": "Completed core system development", "level": 1},
                            {"text": "Successfully integrated with legacy ERP", "level": 1},
                            {"text": "Deployed to staging environment", "level": 1},
                            {"text": "Business Process", "level": 0},
                            {"text": "Finalized user training materials", "level": 1},
                            {"text": "Conducted 3 stakeholder workshops", "level": 1},
                            {"text": "Approved go-live procedures", "level": 1},
                            {"text": "Quality Assurance", "level": 0},
                            {"text": "Completed 89% of test cases", "level": 1},
                            {"text": "Resolved 156 defects", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "challenges",
                    "Current Challenges & Mitigation",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Integration Testing Delays", "level": 0},
                            {"text": "Impact: 1-week delay potential", "level": 1},
                            {"text": "Mitigation: Added weekend testing sessions", "level": 1},
                            {"text": "Resource Availability", "level": 0},
                            {"text": "Impact: Key SME unavailable March 10-17", "level": 1},
                            {"text": "Mitigation: Cross-trained backup resources", "level": 1},
                            {"text": "Change Management", "level": 0},
                            {"text": "Impact: User adoption concerns in Region 2", "level": 1},
                            {"text": "Mitigation: Additional training sessions scheduled", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "budget_status",
                    "Budget Performance",
                    "bullet_list",
                    {
                        "items": [
                            {"text": "Total Budget: $3,200,000", "level": 0},
                            {"text": "Spent to Date: $2,112,000 (66%)", "level": 0},
                            {"text": "Remaining: $1,088,000 (34%)", "level": 0},
                            {"text": "Forecast at Completion: $3,150,000", "level": 0},
                            {"text": "Projected Savings: $50,000 (1.6%)", "level": 0},
                            {"text": "Budget by Category:", "level": 0},
                            {"text": "Development: $1,280,000 (65% utilized)", "level": 1},
                            {"text": "Testing: $420,000 (78% utilized)", "level": 1},
                            {"text": "Training: $180,000 (45% utilized)", "level": 1},
                            {"text": "Infrastructure: $232,000 (85% utilized)", "level": 1}
                        ]
                    }
                )
                .add_content_slide(
                    "next_month",
                    "March 2024 Priorities",
                    "bullet_list",
                    {
                        "items": [
                            "🧪 Complete User Acceptance Testing (March 15)",
                            "📚 Deliver end-user training (March 18-22)",
                            "🔧 Finalize production environment setup",
                            "📋 Conduct go-live readiness assessment",
                            "👥 Execute change management activities",
                            "📊 Prepare go-live communication plan",
                            "🔄 Complete final data migration testing",
                            "✅ Obtain final stakeholder approvals"
                        ]
                    }
                )
                .add_thank_you_slide(
                    contact_info={
                        "email": "pmo@globalmanufacturing.com",
                        "phone": "+1-555-PMO-TEAM",
                        "project_site": "intranet.company.com/digital-transformation"
                    }
                )
                .build())


def generate_all_sample_presentations():
    """Generate all sample presentations and return their configurations"""
    
    templates = {
        'quarterly_business_review': BusinessTemplateExamples.create_quarterly_business_review(),
        'sales_pitch': BusinessTemplateExamples.create_sales_pitch_presentation(),
        'investor_pitch': BusinessTemplateExamples.create_investor_pitch_deck(),
        'project_status': BusinessTemplateExamples.create_project_status_report()
    }
    
    # Export each template to XML for reference
    for name, template in templates.items():
        xml_output = template.to_xml()
        with open(f"{name}_template.xml", 'w') as f:
            f.write(xml_output)
    
    return templates


if __name__ == "__main__":
    print("=== Business Presentation Template Examples ===\n")
    
    # Generate all sample presentations
    templates = generate_all_sample_presentations()
    
    for name, template in templates.items():
        print(f"✅ {name.replace('_', ' ').title()}")
        print(f"   - Slides: {len(template.slides)}")
        print(f"   - Theme: {template.theme.value}")
        print(f"   - Company: {template.company}")
        print(f"   - XML exported to: {name}_template.xml\n")
    
    print(f"Generated {len(templates)} complete business presentation templates!")
    print("Each template includes:")
    print("- Professional slide layouts")
    print("- Business-appropriate content structure")
    print("- Consistent branding and styling")
    print("- Ready-to-use data placeholders")