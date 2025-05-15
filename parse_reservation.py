import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Make sure your .env file is in the project directory.")

# Initialize OpenAI client without custom HTTP client to avoid proxy issues
client = OpenAI(api_key=api_key, http_client=None)

def parse_reservation_request(prompt: str) -> dict:
    system_prompt = """
    You are a helpful assistant that extracts reservation information from natural language.
    Return a JSON object with the following keys: restaurant, date, time, party_size, and location (if available).
    Example:
    {
      "restaurant": "Nobu",
      "date": "2025-05-17",
      "time": "19:00",
      "party_size": 2,
      "location": "Los Angeles"
    }
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("⚠️ Failed to parse response as JSON:", e)
        print("Raw response content:\n", content)
        return {}
