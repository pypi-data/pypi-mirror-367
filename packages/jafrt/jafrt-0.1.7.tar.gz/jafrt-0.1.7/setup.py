from setuptools import setup, find_packages
import pathlib

CURRENT_DIR = pathlib.Path(__file__).parent
long_description = (CURRENT_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="jafrt",
    version="0.1.7",
    author="نام شما",
    author_email="email@example.com",
    description="پکیج چندسکویی پایتون برای تمام پلتفرم‌ها",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jafrt",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
    install_requires=[
    ],
    extras_require={
        "full": ["numpy", "pandas"],
        "mobile": [],
    },
    include_package_data=True,
    package_data={
        "jafrt": ["*.json", "*.txt"],
    },
    entry_points={
        "console_scripts": [
            "jafrt-cli=jafrt.cli:main",
        ],
    },
)