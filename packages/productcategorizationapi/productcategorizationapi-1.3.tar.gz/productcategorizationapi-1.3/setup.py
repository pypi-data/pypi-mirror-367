from setuptools import setup, find_packages
from os.path import abspath, dirname, join

# Fetches the content from README.md
# This will be used for the "long_description" field.
README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()

setup(
    # The name of project.
    # pip install productcategorizationapi
    name="productcategorizationapi",

    # The version of your project.
    version="1.3",

    packages=find_packages(exclude="tests"),

    description="product categorization API",

    long_description=README_MD,

    long_description_content_type="text/markdown",

    url="https://www.productcategorization.com",

    author_name="Samo",
    author_email="info@productcategorizationapi.com",

    # Classifiers help categorize your project.
    # For a complete list of classifiers, visit:
    # https://pypi.org/classifiers
    # This is OPTIONAL
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: GPU :: NVIDIA CUDA :: 11.3","Environment :: GPU :: NVIDIA CUDA :: 11.0", "Environment :: GPU :: NVIDIA CUDA",   "Environment :: GPU :: NVIDIA CUDA :: 11.2","Environment :: GPU :: NVIDIA CUDA :: 10.1", 
        "Programming Language :: Python :: 3 :: Only"
    ],

    keywords="product categorization, classification, categorization",
)