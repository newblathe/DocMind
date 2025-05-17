import pytest
import sys
from pathlib import Path

# Add the project root to the Python path so local modules can be imported
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import the extract_themes function from the services module
from backend.app.services.theme_identifier import extract_themes


def test_extract_themes_manual():
    """
    Unit test for the extract_themes function using sample document responses.

    The test also prints the extracted themes and formatted chat summary for visual inspection.
    """

    # Simulated LLM-extracted answers from music-related documents
    sample_responses = [
        {"doc_id": "DOC001", "answer": "The song's structure borrows heavily from jazz progressions, incorporating modal interchange between Dorian and Mixolydian modes."},
        {"doc_id": "DOC002", "answer": "The record introduced a complex time signature shift from 4/4 to 7/8, which reflects experimental rhythmic techniques."},
        {"doc_id": "DOC003", "answer": "The producer used analog compression techniques to retain warmth while meeting modern loudness standards for streaming platforms."},
        {"doc_id": "DOC004", "answer": "Digital mastering was employed with multiband compression to prepare the album for international release on Spotify and Apple Music."},
        {"doc_id": "DOC005", "answer": "The band's new album critiques the commercialization of music and emphasizes creative independence through self-publishing."},
        {"doc_id": "DOC006", "answer": "A thematic transition occurs in track 4, where orchestration shifts from minimal acoustic guitar to full string arrangements."},
        {"doc_id": "DOC007", "answer": "The artist's latest release explores vocal layering with harmonic intervals and pitch modulation to enhance emotional depth."},
        {"doc_id": "DOC008", "answer": "Streaming platform algorithms favored shorter tracks, prompting the label to suggest tighter track durations under 3 minutes."},
        {"doc_id": "DOC009", "answer": "Live performances introduced improvisational solos not found in the studio versions, showcasing the band's jazz influences."},
        {"doc_id": "DOC010", "answer": "The music video accompanying the single used visual storytelling that matched the lyrical themes of isolation and nostalgia."}
    ]

    # Extract common themes
    common_themes = extract_themes(sample_responses)

    # Print themes for manual verification
    print("\n=== COMMON THEMES ===")
    print(common_themes)