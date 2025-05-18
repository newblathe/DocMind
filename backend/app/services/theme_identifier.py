from typing import List, Dict
from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
assert api_key, "Set the GROQ_API_KEY environment variable."
client = Groq(api_key=api_key)

# Group document-level answers into recurring high-level themes and format them
def extract_themes(responses: List[Dict[str, str]]) -> str:
    """
    Identifies recurring themes across multiple document-level answers
    and returns a well-formatted summary.

    Parameters:
    - responses (List[Dict[str, str]]): List of dictionaries with keys 'doc_id' and 'answer'.

    Returns:
    - summary (str): A formatted textual summary of all themes.
    """

    # Combine document answers into a single block
    combined_text = "\n".join([f"{r['doc_id']}: {r['answer'][:300]}" for r in responses])

    # Prompt instructs the LLM to:
    # - Group answers into themes
    # - Include all document IDs
    # - Format the output exactly as shown — no introductions, no JSON
    prompt = f"""
You are an AI assistant. Analyze the following document-based answers and identify common themes in this exact format only.

IMPORTANT: Include **every document ID**. Do not skip any document. If a document does not match a major theme, create a seperate theme and include it.

Do NOT include: greetings, step numbers, JSON, labels, introductions, extra text, notes or chat.
Only return the common themes, using this structure exactly:

Theme X - [Concise Theme Title]:
Documents (DOC001, DOC002, ......) highlights or proposes or justifies or lacks related information.....

Now  identify common themes in the following answers:
{combined_text}
"""
    try:
        # Send the prompt to Groq LLM for response
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract and clean the raw LLM response
        common_themes = completion.choices[0].message.content.strip()
    except Exception as e:
        print("Failed to extract themes:", e)
        common_themes = "No themes could be extracted due to an error."
    return common_themes
