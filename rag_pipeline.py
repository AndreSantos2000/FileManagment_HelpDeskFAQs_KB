from openai import OpenAI
#from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import fitz  # PyMuPDF
import os

client = OpenAI(base_url="https://5125-213-30-68-70.ngrok-free.app", api_key="lm-studio")

# 1. Embedding function
def get_embedding(text, model="granite-3.1-8b-instruct"):
    text = text.replace("\n", " ")
    return client.embeddings.create(model=model, input=[text], encoding_format="float").data[0].embedding

# 2. Load + embed PDF content
def build_vector_store(filepaths):
    vector_store = []

    for filepath in filepaths:
        with fitz.open(filepath) as doc:
            for page in doc:
                text = page.get_text()
                chunks = split_text(text)
                for chunk in chunks:
                    embedding = get_embedding(chunk)
                    vector_store.append({
                        "chunk": chunk,
                        "embedding": embedding,
                        "source": os.path.basename(filepath)
                    })

    return vector_store

# 3. Basic chunking
def split_text(text, max_tokens=300):
    import re
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len((current + sentence).split()) > max_tokens:
            chunks.append(current.strip())
            current = sentence
        else:
            current += " " + sentence
    if current:
        chunks.append(current.strip())
    return chunks

# 4. Querying vector store
def query_rag(question, vector_store, top_k=3):
    q_embedding = get_embedding(question)
    similarities = []

    for item in vector_store:
        sim = cosine_similarity(
            [q_embedding],
            [item["embedding"]]
        )[0][0]
        similarities.append((sim, item))

    top_matches = sorted(similarities, key=lambda x: x[0], reverse=True)[:top_k]
    context = "\n\n".join([m[1]["chunk"] for m in top_matches])

    return run_llm_with_context(context, question)

# 5. Ask the LLM
def run_llm_with_context(context, question):
    system_prompt = "You are a helpful assistant. Use the following context to answer the question:\n\n" + context
    response = client.chat.completions.create(
        model="granite-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

###### Search logic ######
def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_similar(query, vector_store, top_k=3):
    query_vector = get_embedding(query)
    scored = [(cosine_similarity(query_vector, item["embedding"]), item) for item in vector_store]
    scored = sorted(scored, key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_k]]