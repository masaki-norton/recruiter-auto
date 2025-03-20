from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import sqlite3
from contextlib import closing
import json

def extract_notes_from_call(transcript: str):
    """ This method extracts meeting notes from a transcript call between a recruiter
    and a candidate.
    Specifically, it returns raw notes in detail, and a next_action item to
    determine the next required action from either keep_in_touch, pitch_company,
    or cv_update.
    """

    model = ChatOpenAI(model="gpt-4o", temperature=0)

    class NextActionType(str, Enum):
        FOLLOW_UP = "follow_up"
        SCHEDULE_INTERVIEW = "schedule_interview"
        NO_ACTION = "no_action"

    class NoteData(BaseModel):
        note_text: str = Field(description="Main content of the note")
        next_action: NextActionType = Field(
            description="The next action to take with this candidate"
        )

    sys_msg = """
    You are an assistant who outputs JSON data for the user in the specified schema.
    You will be given a piece of text from the user which indicates a transcript of a call
    between a recruiter and a potential candidate.

    You are to create meeting minutes such that enough information can be gathered
    from your output to create a candidate CV, or track any relevant information
    about the candidate in the applicant tracking system. These minutes should be
    returned in the "notes" field of a json object. dont worry about the text getting too long,
    make sure it contains enough relevant info that you can pick up from the call.

    You should also output one of three next actions, depending on the contents of the call.
    The three options are:
    1. keep_in_touch, which is used when it is deemed that the candidate is no good
    match for current positions that the recruiter is offering.
    2. pitch_company, which is used when a specific company is spoken about during the
    meeting and the candidate is happy to either know more or apply.
    3. update_cv, which is used when updating cv is disscusssed in the call.

    Make sure your output is in JSON format with keys "notes" and "next_action"

    Also the entries into notes should be written not as structured data but more like
    meeting minutes bullet point notes, preserving info as much as possible. However, your
    output should not be a python list, but just a long string. You do not need to
    include personal info such as email address etc as that info is already extracted
    from another method.

    Make sure to include plenty of detail as this is supposed to be a record of meeting minutes.
    """

    human_msg = """
    Here is the transcript: {transcript}
    """

    notes_template = ChatPromptTemplate.from_messages(
        [
            ("system", sys_msg),
            ("human", human_msg)
        ]
    )

    chain = notes_template | model | JsonOutputParser(pydantic_object=NoteData)

    notes_json = chain.invoke({"transcript": transcript})

    return notes_json

def add_new_note_from_json(payload):
    """ This method will add notes from a call into a db. The input is a json object
    with the following strings:
    """

    candidate_id = payload["candidate_id"]
    notes = payload["notes"]
    next_action = payload["next_action"]

    if isinstance(candidate_id, str):
        candidate_id = int(candidate_id)

    db_path = "candidate.db"

    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Notes (candidate_id, note_text, next_action)
            VALUES (?, ?, ?)
        """, (candidate_id, notes, next_action))
        conn.commit()

    return (candidate_id, next_action)

if __name__ == "__main__":
    DB_PATH = "candidate.db"
    with open("michael_scott.txt", "r") as file:
        transcript = file.read()
    json_output = extract_notes_from_call(transcript=transcript)
    print(f"{json_output = }")
    candidate_id = "1"
    candidate_id, next_action = add_new_note_from_json(
        db_path=DB_PATH,
        candidate_id=candidate_id,
        notes_json=json_output,
    )
    print(f"{next_action = }")
