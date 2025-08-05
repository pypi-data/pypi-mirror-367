from setuptools import setup, find_packages

setup(
    name="skope-sdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="Skope",
    author_email="connor@useskope.com",
    description="Python SDK for the Skope API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/skope/skope-sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 