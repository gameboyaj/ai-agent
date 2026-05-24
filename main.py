from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import argparse

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("API key not found / invalid")

client = genai.Client(api_key=api_key)

messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
)

if not response.usage_metadata:
    raise RuntimeError("API key not found / invalid")

if args.verbose:
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
print(response.text)