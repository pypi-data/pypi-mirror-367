import tiktoken

def num_tokens_from_string(string: str, model: str = "llama-3.1-8b-instant") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(string))