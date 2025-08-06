from setuptools import setup, find_packages

setup(
    name="optimizer-rag",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.16",
        "groq",
        "tiktoken",
        "numpy",
        "scikit-learn",
        "sentence-transformers",
        "streamlit",
        "python-dotenv"
    ],
    author="Mihir Kapile",
    author_email="mihirkapile@gmail.com",
    description="A document compression and optimization library using Groq LLMs and LangChain",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
