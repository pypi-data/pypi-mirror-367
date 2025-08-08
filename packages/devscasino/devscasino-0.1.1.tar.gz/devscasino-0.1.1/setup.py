from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="devscasino",
    version="0.1.1",
    author="Your Name",
    author_email="you@example.com",
    description="A simple GUI-based casino slot machine library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/devscasino",  # optional
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
