"""
Setup configuration for eBay Label Printer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ebay-label-printer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automatically prints shipping labels and packing lists from eBay orders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ebay-label-printer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ebay-label-printer=run:main",
        ],
    },
)