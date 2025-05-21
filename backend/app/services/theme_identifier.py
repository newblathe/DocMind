from typing import List, Dict
from groq import Groq
from pathlib import Path

from backend.app.core.logger import logger
from backend.app.core.config import GROQ_API_KEY

# Initialize Groq client

client = Groq(api_key=GROQ_API_KEY)

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

    logger.info(f"Generating themes from {len(responses)} document-level answers...")

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
Documents (DOC001.pdf, DOC002.txt, ......) highlight or propose or justify or lack ......

Documents that have been already included in a theme can again appear in a theme. Also there might be themes that are not common among multiple documents list them as well.

Note: A single document may be relevant to multiple themes and should appear in each applicable theme. Unique themes that apply to only one document should also be included.

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

        logger.info("Theme extraction completed successfully.")

    except Exception as e:
        logger.error("Theme extraction failed.", exc_info=True)
        common_themes = "No themes could be extracted due to an error."
    return common_themes
