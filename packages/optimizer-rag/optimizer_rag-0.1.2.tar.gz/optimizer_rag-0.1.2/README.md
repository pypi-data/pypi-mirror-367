# Optimizer

Optimizer is a Python library for compressing large documents using LLMs like Groq. It provides functionality for summarizing document chunks based on a query, selecting the most relevant summaries, and managing token budgets effectively — ideal for RAG (Retrieval Augmented Generation) applications.

## Features

- Summarize document chunks using Groq models
- Select relevant summaries based on token limits
- Easily integrate with any RAG pipeline

## Installation

```bash
pip install optimizer-groq
```

## Requirements

Make sure the following packages are installed (handled automatically if installing via pip):

```text
langchain>=0.1.16
groq
tiktoken
numpy
scikit-learn
sentence-transformers
python-dotenv
```

## Usage

```python
from optimizer.compressor import compress_chunk

chunks = ["Paragraph 1...", "Paragraph 2...", "Paragraph 3..."]
query = "What are the benefits of renewable energy?"
token_budget = 512

selected = compress_chunk(chunks, query, token_budget)
print(selected)
```

You can also customize the model by injecting the model into the library functions like this.

```python
from openai import OpenAI
from optimizer.compressor import compress_chunk

client = OpenAI(api_key="your-openai-api-key")

chunks = ["Text A...", "Text B..."]
query = "Summarize risks."
token_budget = 400

summaries = compress_chunk(chunks, query, token_budget, client=client, model="gpt-4")
```


## Environment Setup

Set your Groq API key in a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

