from setuptools import setup, find_packages

setup(
    name="yadumair",
    version="0.1.0",
    description="A simple package to generate bedtime stories using OpenAI GPT-5",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "openai"  # Ensure openai library is installed
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
