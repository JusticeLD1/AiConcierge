import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please add it to your .env file.")

# Initialize OpenAI client with default settings
# This avoids explicit http_client configuration which is causing the proxy error
client = OpenAI(api_key=api_key)

def parse_reservation_request(prompt: str) -> dict:
    """
    Parse a natural language reservation request into structured data.
    
    Args:
        prompt (str): Natural language description of reservation request
        
    Returns:
        dict: Structured reservation data including restaurant, date, time, etc.
    """
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

    try:
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
            
    except Exception as e:
        print(f"⚠️ Error communicating with OpenAI API: {e}")
        return {}