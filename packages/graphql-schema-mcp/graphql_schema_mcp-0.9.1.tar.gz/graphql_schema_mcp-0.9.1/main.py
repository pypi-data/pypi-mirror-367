import hashlib
import re

import faiss
import numpy as np
import torch
from fastmcp import FastMCP
from sentence_transformers import SentenceTransformer

app = FastMCP('GraphQL MCP Server')

# Regex to split GraphQL into chunk by types
regex = re.compile(
    '(?:"(?:"")?[^"]+?(?:"")?"\\s)?^(?:(?:type|interface|input|enum) [\\S\\s]+?}|union [\\S\\s]+?= \\S+? (?:\\| \\S+?\\s)+)',
    flags=re.M)

device = "mps" if torch.backends.mps.is_available() else "cpu"
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
embedding_cache = {}


def get_embeddings(path: str) -> np.ndarray:
    with open(path, 'r') as f:
        content = f.read()
    digest = hashlib.sha3_224()
    digest.update(content.encode('utf-8'))
    digest = digest.hexdigest()
    if path not in embedding_cache.keys() or embedding_cache[path]['hash'] != digest:
        items = regex.findall(content)
        embeddings = embedder.encode([f'query: {item}' for item in items])
        embedding_cache[path] = {'hash': digest, 'embeddings': np.array(embeddings).astype(np.float32), }

    return embedding_cache[path]['embeddings']


@app.tool(description="Searches for a phrase and returns appropriate graphQL type")
def search(absolute_path: str, phrase: str, ) -> dict[str, list[tuple[float, str]]]:
    with open(absolute_path, 'r') as f:
        content = f.read()
    items = regex.findall(content)

    embedded_matrix = get_embeddings(absolute_path)

    dims = embedded_matrix.shape[1]
    index = faiss.IndexFlatIP(dims)
    faiss.normalize_L2(embedded_matrix)
    index.add(embedded_matrix)

    formatted_query = f'query: {phrase}'
    query_embeddings = embedder.encode([formatted_query], normalize_embeddings=True)
    query_embeddings = np.array(query_embeddings).astype(np.float32)

    k = 5
    scores, indices = index.search(query_embeddings, k)

    return {"result": [(scores[0][i].item(), items[indices[0][i]]) for i in range(len(indices[0]))]}


def main():
    app.run(transport="stdio", show_banner=False)


if __name__ == '__main__':
    main()
