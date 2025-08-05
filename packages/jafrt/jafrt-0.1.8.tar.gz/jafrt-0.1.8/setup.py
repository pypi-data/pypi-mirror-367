from setuptools import setup, find_packages
from pathlib import Path

current_dir = Path(__file__).parent
long_desc = (current_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="jafrt",
    version="0.1.8",
    author="Your Name",
    author_email="your@email.com",
    description="Multi-platform color print package for Python",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jafrt",
    packages=find_packages(include=['jafrt*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "full": ["numpy>=1.21.0", "pandas>=1.3.0"],
        "windows": ["colorama>=0.4.6"],
    },
    package_data={
        "jafrt": ["*.json", "*.txt", "*.md"],
    },
    entry_points={
        "console_scripts": ["jafrt=jafrt.cli:main"],
    },
    zip_safe=False,
)