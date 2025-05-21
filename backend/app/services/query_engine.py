from typing import List, Dict

from groq import Groq
from pathlib import Path
import json
import re
from tabulate import tabulate

from backend.app.services.vector_store import search_top_k_chunks
from backend.app.core.logger import logger

from backend.app.core.config import GROQ_API_KEY

# Load environment variables from .env file

# Initialize Groq client using the API key
client = Groq(api_key=GROQ_API_KEY)

def extract_answers_from_docs(user_query: str, doc_ids: List[str]) -> List[Dict[str, str]]:
    """
    Extracts relevant answers and citations from a set of documents based on a user query using Groq's LLM.

    For each document, this function prompts the LLM to:
    1. Generate the most relevant answer to the user-provided question.
    2. Identify and return a citation indicating where in the document the answer appears (e.g., paragraph number).

    The LLM is instructed to preserve any referenced clauses, sections, or numbered parts (legal or non-legal)
    exactly as they appear in the document text.

    Parameters:
    - user_query (str): The user's question or prompt to guide the extraction.
    - doc_ids (List[str]): A list which contains the doc_id for each document.

    Returns:
    - List[Dict[str, str]]: A list of dictionaries, each containing:
        - 'doc_id': The ID of the document.
        - 'answer': The LLM-extracted answer relevant to the user query.
        - 'citation': The approximate paragraph or sentence location of the answer within the document.
    """
    logger.info(f"Extracting answers for query: '{user_query}' across {len(doc_ids)} document(s).")

    results = []

    # Iterate through all documents and extract answer + citation from each
    for doc_id in doc_ids:
        logger.info(f"Retrieving top chunks for document: {doc_id}")
        top_chunks = search_top_k_chunks(doc_id, user_query, k=5)

        if not top_chunks:
            logger.warning(f"No relevant chunks found for {doc_id}. Skipping.")
            continue

        combined_chunks = "\n".join([f"[Para {c['chunk_index']+1}]: {c['text']}" for c in top_chunks])

        prompt = f"""
You are an AI assistant. Given the following paragraphs from a document and a user's question, perform two tasks with maximum attention to detail:

1. Extract the **most relevant, complete and context-rich answer** from the paragraphs.  
   - Your answer MUST include **every important keyword, clause, dates, section reference, or phrase** that supports or elaborates on the answer.  
   - If the paragraphs reference numbered parts, sections, clauses, dates or labeled items (e.g., “Section 2 of the audit”, “Clause 49”), you MUST reproduce them **exactly as written** — no paraphrasing or simplification.  
   - Include all **supporting phrases**, **related justifications**, and **legal or technical terminology**. Do not summarize.  
   - If no relevant answer exists, set the answer as `"no relevant information found"`.

2. Provide a citation for where in the document the answer came from:  
   - Use paragraph numbers (e.g., Para 4) or sentence numbers (e.g., Sentence 3) whichever is **most specific and accurate**.
   - If possible, use exact references based on the document structure. Each paragraph is clearly separated.
   - If the document is not relevant, set the citation as `"Unknown"`.

Document ID: {doc_id}

Paragraphs:

{combined_chunks}

User Question:
{user_query}

RESPONSE FORMAT (STRICT):
- Respond with ONLY valid **single-line JSON**.
- DO NOT include any extra text, explanation, formatting, or markdown.
- Ensure proper escaping of all quotes and characters.

Must Return only valid JSON strictly in this format:
{{"answer":"Your detailed answer here.","citation":"Para X"}}

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
                logger.warning(f"Empty response received from LLM for document: {doc_id}")
                continue
            
            # Extract clean JSON using RegEX
            json_match = re.search(r'{\s*"answer"\s*:\s*".*?",\s*"citation"\s*:\s*".*?"\s*}', content, re.DOTALL)
            if not json_match:
                logger.warning(f"Invalid JSON format received for document: {doc_id}")
                continue

            parsed = json.loads(json_match.group())
            answer = parsed.get("answer", "").strip()
            citation = parsed.get("citation", "").strip()

            # Add result only if a meaningful answer is found
            if answer.lower() != "no relevant information found":
                results.append({
                    "doc_id": doc_id,
                    "answer": answer,
                    "citation": citation
                })
                logger.info(f"Answer extracted for {doc_id}: {citation}")
            else:
                results.append({
                    "doc_id": doc_id,
                    "answer": f"No relevant answer found",
                    "citation" : "Unkonown"

                })
                logger.info(f"No relevant answer found in {doc_id}")

        except Exception as e:
            print(f"Failed to process {doc_id}: {e}")
            continue
    
    logger.info(f"Answer extraction complete. Total successful answers: {len(results)}")
    return results
