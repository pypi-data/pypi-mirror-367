from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rexi-py",
    version="0.1.4",
    author="RexiAPI Team",
    author_email="rexidotsh@outlook.com",
    description="A Python client library for Rexi API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rexi-sh/rexi-py",
    project_urls={
        "Website": "https://rexi.sh",
        "Documentation": "https://rexi.sh/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0",  # For async HTTP requests
        "websockets>=10.0",  # For WebSocket connections
    ],
)
