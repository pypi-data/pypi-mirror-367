from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="outlier_cleaner",
    version="1.1.2",
    author="Subashanan Nair",
    author_email="subaashnair12@gmail.com",  # Replace with your email
    description="A Python package for detecting and removing outliers in data using various statistical methods and advanced distribution analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SubaashNair/OutlierCleaner",  # Updated with correct URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.2.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "scipy>=1.6.0",
        "tqdm>=4.60.0",
    ],
)