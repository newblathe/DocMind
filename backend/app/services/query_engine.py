from typing import List, Dict
import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import json
import re
from tabulate import tabulate

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client using the API key
api_key = os.getenv("GROQ_API_KEY")
assert api_key, "Set the GROQ_API_KEY environment variable."
client = Groq(api_key=api_key)

def extract_answers_from_docs(user_query: str, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Extracts relevant answers and citations from a set of documents based on a user query using Groq's LLM.

    For each document, this function prompts the LLM to:
    1. Generate the most relevant answer to the user-provided question.
    2. Identify and return a citation indicating where in the document the answer appears (e.g., paragraph number).

    The LLM is instructed to preserve any referenced clauses, sections, or numbered parts (legal or non-legal)
    exactly as they appear in the document text.

    Parameters:
    - user_query (str): The user's question or prompt to guide the extraction.
    - documents (List[Dict[str, str]]): A list of dictionaries where each contains:
        - 'doc_id': Unique identifier for the document.
        - 'text': Full document content (preprocessed).

    Returns:
    - List[Dict[str, str]]: A list of dictionaries, each containing:
        - 'doc_id': The ID of the document.
        - 'answer': The LLM-extracted answer relevant to the user query.
        - 'citation': The approximate paragraph or sentence location of the answer within the document.
    """
    results = []

    # Iterate through all documents and extract answer + citation from each
    for doc in documents:
        doc_id = doc.get("doc_id")
        text = doc.get("text")

        if not doc_id or not text:
            continue

        prompt = f"""
You are an AI assistant. Given the following document content and a user's question, perform two tasks:

1. Extract the most relevant answer from the document and if there is no relevant answer, still answer that the document is not relevant to the query.

IMPORTANT: If the document includes any references to numbered parts, sections, clauses, or labeled items
(e.g., “Section 2 of the audit”, “Part 4 of the document”, “Clause 49”), you MUST include them in exactly the same words as were used originally in the answer — exactly as they appear in the document. 
This applies to both legal and non-legal contexts.
Do NOT rephrase or skip them.
2. Provide a citation for where in the document the answer came from — this could be a page number (e.g., Page 2), paragraph number (e.g., Para 4), or sentence number (e.g., Sentence 3), whichever is most appropriate based on the document layout and if the answer is not relevant make the citation as unknown.

Document ID: {doc_id}

Document Content:

Each paragraph and sentence in the document is clearly separated. Use paragraph numbers (e.g., Para 1, Para 2), sentence positions (e.g., Sentence 3), or page numbers (e.g., Page 2) as reference for your citation, whichever is most precise based on the document structure.

{text[:3000]}

User Question:
{user_query}

RESPONSE FORMAT (Strict):
- Respond with ONLY valid JSON on a single line.
- Do NOT include extra text, explanations, or formatting.
- Escape any quotes or special characters properly.

Correct format:
{{"answer":"Your answer here.","citation":"Para X"}}

Do not return markdown, backticks, or multi-line output.
"""

        try:
            # Send the prompt to the Groq LLM for response
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            )


            # Extract and clean the raw LLM response
            content = response.choices[0].message.content.strip()

            if not content:
                print(f"Empty response for {doc_id}")
                continue
            
            # Extract clean JSON using RegEX
            json_match = re.search(r'{\s*"answer"\s*:\s*".*?",\s*"citation"\s*:\s*".*?"\s*}', content, re.DOTALL)
            if not json_match:
                print(f"No valid JSON found in response for {doc_id}")
                continue

            parsed = json.loads(json_match.group())
            answer = parsed.get("answer", "").strip()
            citation = parsed.get("citation", "").strip()

            # Add result only if a meaningful answer is found
            if answer and answer.lower() != "no relevant information found":
                results.append({
                    "doc_id": doc_id,
                    "answer": answer,
                    "citation": citation or "Unknown"
                })

        except Exception as e:
            print(f"Failed to process {doc_id}: {e}")
            continue

    return results
