from setuptools import setup, find_packages

setup(
    name="weather_lib",             # Must be unique on PyPI
    version="0.1.0",
    author="Rajesh Neupane",
    author_email="rajeshneupane7@gmail.com",
    description="package to download the historical weatehr data uisng api",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
      # Optional
    packages=find_packages(),             # Automatically find your_package
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
