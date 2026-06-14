# Milestone 5 — Grounded Response Generation
#
# Summary of steps:
#   1. Accept a user query
#   2. Retrieve top-5 relevant chunks from ChromaDB via retrieve()
#   3. Format chunks into a numbered context block with source labels
#   4. Send context + query to Groq llama-3.3-70b-versatile with a grounding prompt
#   5. Return dict: {answer, sources, chunks}
#
# Grounding is enforced in the system prompt: the model is instructed to answer
# ONLY from the provided documents and explicitly decline if context is insufficient.
#
# Time complexity:  O(k) for retrieval + O(1) for single Groq API call
# Space complexity: O(k) for k retrieved chunks held in memory per query

import os
from groq import Groq
from dotenv import load_dotenv
from retrieval import retrieve

load_dotenv()  # loads GROQ_API_KEY from .env

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"

# System prompt enforces grounding — model must answer from documents only
SYSTEM_PROMPT = """You are an assistant that answers questions about UIUC professors \
and courses using only student reviews from Rate My Professors.

Rules:
- Answer using ONLY the information in the provided documents. Do not use outside knowledge.
- If the documents do not contain enough information to answer, respond exactly with: \
"I don't have enough information on that based on the available reviews."
- Be direct and specific — quote or closely paraphrase what reviewers actually said."""


def format_context(chunks):
    """
    Format retrieved chunks into a numbered context block for the prompt.
    Each chunk is labeled with its source file, professor, and course.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        label = f"[{chunk['source']}]"
        text = chunk["text"]  # keep full text including professor/course metadata line
        context_parts.append(f"{label}\n{text}")
    return "\n\n".join(context_parts)


def ask(query):
    """
    Full RAG pipeline: retrieve -> format context -> generate grounded response.
    Returns a dict: {answer: str, sources: list[str], chunks: list[dict]}
    """
    # Step 1: retrieve relevant chunks
    chunks = retrieve(query)

    # Step 2: format into context block
    context = format_context(chunks)

    # Step 3: build user message with context + query
    user_message = f"""Documents:
{context}

Question: {query}"""

    # Step 4: call Groq — low temperature for factual, grounded answers
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ],
        max_tokens=1000,
        temperature=0.1
    )

    answer = response.choices[0].message.content

    # Deduplicate source filenames for the interface display
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  chunks
    }


if __name__ == "__main__":
    # End-to-end grounding test — run 2 good queries + 1 out-of-scope query
    test_queries = [
        "What do students say about Graham Evans's lectures in CS225?",
        "How does Wade Fagen approach teaching based on student reviews?",
        "What is the best restaurant near the UIUC campus?"  # out-of-scope: should decline
    ]

    for query in test_queries:
        print(f"\nQ: {query}")
        print("-" * 60)
        result = ask(query)
        print(result["answer"])
        print()