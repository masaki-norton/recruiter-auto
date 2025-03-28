from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import sqlite3
from contextlib import closing

import json

def extract_work_experiences(transcript: str):
    """ This method extracts work experiences from a transcript call between a recruiter
    and a candidate.
    Specifically, it returns a list of json objects, each containing the company,
    tenure duration, and any description of the position, which are listed as if
    they are written on a CV.
    """
    load_dotenv()

    model = ChatOpenAI(model="gpt-4o", temperature=0)

    class WorkExperienceSQLEntry(BaseModel):
        company: str = Field(description="the company that the candidate worked at during this time")
        start_date: str = Field(description="start date working at company, in ISO8601 format")
        end_date: str = Field(description="end date working at company, in ISO8601 format")
        description: str = Field(description="detailed tenure experience description.")

    class WorkExperience(BaseModel):
        entries: list[WorkExperienceSQLEntry] = Field(description="list of sql entries")

    sys_msg = """
    You are an assistant who outputs JSON data for the user in the specified schema.
    You will be given a piece of text from the user which indicates a transcript of a call
    between a recruiter and a potential candidate.

    You are to create work experience sql entries, where each entry covers a tenure at one company.
    Internal moves still stay within the same sql entry into the database. The output should
    have the following fields:
    company: the company name
    start_date: ISO8601 standard tenure start date
    end_date: ISO8601 standard tenure end date
    description: detailed tenure experience description.

    In the description field, you should structure your string as if it were written on a resume.
    An example is shoown below:
    Junior Software Engineer (2005–2007)
        Built internal tools using Python and Flask to streamline team workflows.
        Designed relational database schemas with PostgreSQL for data tracking.
        Reduced manual reporting time by 20% through automation scripts.
    Software Engineer (2007–2009)
        Developed a customer-facing portal using AngularJS, improving client satisfaction.
        Integrated analytics tracking with Google Analytics, providing actionable insights.
        Trained three new hires on version control and deployment processes.

    Given the meeting transcript given by the user, create a list of work experience sql entries
    following the instructions above. Your completed reply should be a json object with
    a single key "entries" and a value which is a list of the json schema for work experience entries.

    Do not forget that each sql entry should cover the candidate's whole tenure at one company,
    so if they get a promotion halfway between, that should be noted in the description as well.
    Do not create separate sql entries for the same position when there is an internal change
    in their role.

    Do not add dates to ISO8601 format dates, if not specified. If the month is only specified,
    list the date in YYYY-MM format only, no dates. If there is no end date given, make sure you
    write NULL in all caps so the sql db recognizes that it should be Null. But you must
    always have a start date.
    """

    human_msg = """
    Here is the meeting transcript: {transcript}
    """

    work_exp_template = ChatPromptTemplate.from_messages(
        [
            ("system", sys_msg),
            ("human", human_msg),
        ]
    )

    chain = work_exp_template | model | JsonOutputParser(pydantic_object=WorkExperience)

    work_exp_json = chain.invoke({"transcript": transcript})

    return work_exp_json

def add_work_experience_from_json(payload):
    """ This method adds a work_exp_json object into the WorkExperience table.
    The objects get added as new entries into the WorkExperience table.
    This script takes in two input variables:
    1. a candidate_id, which should be a number
    2. a list of work_experience json objects.
    You can pass both variables as strings, as long as they are in the correct
    format since the code will change it to JSON properly before processing.
    """
    # context = json_cleanup(context, "output keys should be candidate_id for the id, and work_experience forr the list of dictionaries which are entries into a db containing company, start_date, end_date, and description")
    # candidate_id = context["candidate_id"]
    # entries = context["work_experience"]

    # if isinstance(candidate_id, str):
    #     candidate_id = int(candidate_id)

    db_path = "candidate.db"

    candidate_id = payload["candidate_id"]
    entries = payload["entries"]

    for entry in entries:
        company = entry["company"]
        start_date = entry["start_date"]
        end_date = entry["end_date"]
        description = entry["description"]

        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO WorkExperience (candidate_id, company, start_date, end_date, description)
                VALUES (?, ?, ?, ?, ?)
            """, (candidate_id, company, start_date, end_date, description))
            conn.commit()

    print(f"Added {len(entries)} experience rercords for ID: {candidate_id}")

    return None

if __name__ == "__main__":
    DB_PATH = "candidate.db"
    with open("data/text_minutes/carlos_rivera_minutes.txt", "r") as file:
        transcript = file.read()
    work_experience = extract_work_experiences(transcript=transcript)
    print(f"{work_experience = }")
    candidate_id = 1
    add_work_experience_from_json(db_path=DB_PATH, candidate_id=candidate_id, work_exp_json=work_experience)
