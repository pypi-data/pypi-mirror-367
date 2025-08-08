from setuptools import setup, find_packages

# Load the README as long_description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="apipie",
    version="0.5.0",
    author="Your Name",
    author_email="tmpkokorocks@awsl.uk",
    description="A short description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kokoslabs/apipie",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

