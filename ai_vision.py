import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODELS = os.getenv("GEMINI_MODELS", "gemini-3.8-flash,gemini-3.5-flash-lite").split(",")

PROMPT = """You are given two screenshots of the {company} careers page:
the first image is BEFORE, the second image is AFTER.

Read every job posting visible in each screenshot and return its exact title.
Copy titles exactly as written, so the same job has the same title in both lists.
Ignore everything that is not a job posting: headers, filters, ads, cookie banners,
"Posted X days ago" text, and page numbers."""


class JobsOnPage(BaseModel):
    jobs_before: list[str] = Field(description="Job titles visible in the BEFORE screenshot")
    jobs_after: list[str] = Field(description="Job titles visible in the AFTER screenshot")


def read_jobs(company, before_path, after_path):
    if not GEMINI_API_KEY:
        print("AI is not configured: add GEMINI_API_KEY to .env")
        return None

    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=4, initial_delay=5),
        ),
    )
    contents = [
        types.Part.from_bytes(data=Path(before_path).read_bytes(), mime_type="image/png"),
        types.Part.from_bytes(data=Path(after_path).read_bytes(), mime_type="image/png"),
        PROMPT.format(company=company),
    ]
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=JobsOnPage.model_json_schema(),
        temperature=0,
    )

    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            return JobsOnPage.model_validate_json(response.text)
        except Exception as e:
            print(f"[{company}] AI analysis with {model} failed: {type(e).__name__}: {e}")

    return None