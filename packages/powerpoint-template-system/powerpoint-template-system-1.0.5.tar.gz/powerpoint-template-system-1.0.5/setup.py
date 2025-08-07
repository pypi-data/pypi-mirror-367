"""
Setup configuration for PowerPoint Template System
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="powerpoint-template-system",
    version="1.0.5",
    author="PowerPoint Template System Team",
    author_email="templates@cpro.com",
    description="A comprehensive template system for creating professional business presentations with modern styling, cards, and badges",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cpro/powerpoint-template-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
        "examples": [
            "matplotlib>=3.3.0",
            "pandas>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ppt-template=powerpoint_templates.cli:main",
            "ppt-generate=powerpoint_templates.cli:generate",
        ],
    },
    include_package_data=True,
    package_data={
        "powerpoint_templates": [
            "config/*.json",
            "templates/*.xml",
            "schemas/*.xsd",
        ],
    },
    keywords=[
        "powerpoint", "presentation", "template", "business", "slides", "pptx",
        "cards", "badges", "modern-styling", "gradients", "shadows", "typography",
        "dsl", "domain-specific-language", "visual-generator", "professional"
    ],
    platforms=["any"],
    zip_safe=False,
)