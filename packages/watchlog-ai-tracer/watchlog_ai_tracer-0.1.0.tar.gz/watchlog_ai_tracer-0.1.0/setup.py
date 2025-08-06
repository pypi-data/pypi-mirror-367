from setuptools import setup, find_packages

setup(
    name="watchlog-ai-tracer",
    version="0.1.0",
    license="MIT",
    description="Lightweight Python tracer for Watchlog AI monitoring",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mohammadreza",
    author_email="mohammadnajm75@gmail.com",
    url="https://github.com/Watchlog-monitoring/python-ai-tracer",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "filelock>=3.0.0",
        "dnspython>=2.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
