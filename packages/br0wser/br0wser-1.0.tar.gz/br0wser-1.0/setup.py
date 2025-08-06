from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="br0wser",
    version="1.0",
    author="Mateus Mesquita",
    author_email="tommy0stardust@gmail.com",
    description="Buscador",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tommyst0/br0wser",  
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "newspaper3k",
        "sumy",
    ],
)