from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import sqlite3
from contextlib import closing

import json

load_dotenv()

def extract_candidate_info(transcript: str):
    """ This method extracts basic candidate info from a call transcript.
    Specifically, it returns first name, last name, and email.
    """

    model = ChatOpenAI(model="gpt-4o", temperature=0)

    class Candidate(BaseModel):
        first_name: str = Field(description="candidate first name")
        last_name: str = Field(description="candidate last name")
        email: str = Field(description="candidate email address")

    sys_msg = """
    You are an assistant who outputs valid JSON data strictly following the given schema.
    Your output must use double quotes for all keys and string values.
    You will be given a transcript of a call between a recruiter and a candidate.
    Extract and output the following fields in JSON:
    - Candidate first name (first_name)
    - Candidate last name (last_name)
    - Candidate email address (email)
    """

    human_msg = """
    Here is the transcript: {transcript}
    """

    extract_template = ChatPromptTemplate.from_messages(
        [
            ("system", sys_msg),
            ("human", human_msg)
        ]
    )

    chain = extract_template | model | JsonOutputParser(pydantic_object=Candidate)
    candidate_json = chain.invoke({"transcript": transcript})

    return candidate_json

def add_new_cand_from_json(candidate_json):
    """This method takes in a candidate_json, which includes first name last name
    and email address, and adds the new candidate to the main database into the Candidates table.
    """
    if isinstance(candidate_json, str):
        candidate_json = json.loads(candidate_json.replace("'", '"'))

    db_path = "candidate.db"
    first_name = candidate_json['first_name']
    last_name = candidate_json['last_name']
    email = candidate_json['email']

    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Candidates (first_name, last_name, email)
            VALUES (?, ?, ?)
        """, (first_name, last_name, email))
        candidate_id = cursor.lastrowid
        conn.commit()

    return candidate_id

if __name__ == "__main__":
    DB_PATH = "candidate.db"
    with open("michael_scott.txt", "r") as file:
        transcript = file.read()
    json_output = extract_candidate_info(transcript=transcript)
    print(f"{json_output = }")
    new_id = add_new_cand_from_json(db_path=DB_PATH, candidate_json=json_output)
    print(f"{new_id = }")
