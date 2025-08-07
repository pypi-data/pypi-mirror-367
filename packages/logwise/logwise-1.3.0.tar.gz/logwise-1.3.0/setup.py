from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logwise",
    version="1.3.0",
    author="Prateek Gupta",
    author_email="",
    description="A clean, colorful terminal logger with boxed message support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prateekgupta1089/logwise",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    license="MIT",
)