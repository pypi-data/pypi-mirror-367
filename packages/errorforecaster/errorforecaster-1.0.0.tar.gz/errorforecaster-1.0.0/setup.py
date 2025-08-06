"""
ErrorForecaster setup.py
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="errorforecaster",
    version="1.0.0",
    author="tikisan",
    author_email="",
    description="コード内の潜在的なバグ発生確率を予測するPythonライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/errorforecaster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "regex>=3.0.0",
        "rich>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "errorforecaster=errorforecaster.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 