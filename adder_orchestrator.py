import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from add_new_candidate import extract_candidate_info, add_new_cand_from_json
from add_new_note import extract_notes_from_call, add_new_note_from_json

load_dotenv()

def add_first_time_candidate(transcript: str):
    """
    This function should be called when a new candidate is added to the database.
    It is for the unique case where the candidate is brand new in the system,
    and requires the below steps to be executed in order:
    1. Add to candidates table
    """

    candidate_info_json = extract_candidate_info(transcript=transcript)
    new_id = add_new_cand_from_json(candidate_json=candidate_info_json)

    notes = extract_notes_from_call(transcript=transcript)
    notes["candidate_id"] = new_id
    add_new_note_from_json(notes)

    return notes, type(notes)

if __name__ == "__main__":
    with open("test_data/transcripts/michael_scott_minutes.txt", "r") as file:
        transcript = file.read()
    output = add_first_time_candidate(transcript=transcript)
    print(output)
