"""Setup script for dashcam manager application."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="dashcam-manager",
    version="1.0.0",
    description="Linux desktop application for managing dashcam videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Terry",
    python_requires=">=3.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "PyGObject>=3.46.0",
        "Pillow>=10.0.0",
        "python-vlc>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "requests-mock>=1.11.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dashcam-manager=ui.main_window:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Video",
    ],
)
