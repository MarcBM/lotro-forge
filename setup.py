from setuptools import setup, find_packages

setup(
    name="lotro_forge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your project dependencies here
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "coverage>=7.3.0",
        ],
    },
    python_requires=">=3.9",
    author="MarcBM",
    description="A tool for working with LOTRO item data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MarcBM/lotro_forge",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 