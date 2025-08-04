from setuptools import setup, find_packages

setup(
    name="kraken_request",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "stem>=1.8.0",
        "PySocks>=1.7.1"
    ],
    author="Anonymous Developer",
    author_email="anonymous@example.com",
    description="Secure anonymous requests and phone number protection",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="anonymizer tor security privacy",
    url="https://github.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Internet :: Proxy Servers"
    ],
    python_requires='>=3.6',
)
