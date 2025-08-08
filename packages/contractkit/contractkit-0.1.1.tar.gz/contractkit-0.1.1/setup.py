from setuptools import setup, find_packages

setup(
    name="contractkit",
    version="0.1.1",
    description="A Python library for contract analysis using LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Shubham Kaushik",
    author_email="eskaykaushik2@gmail.com",
    url="https://github.com/Eskaykaushik/contractKit.git",
    packages=find_packages(),
    install_requires=[
        "openai",     # or groq if you use it
        "PyPDF2",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
