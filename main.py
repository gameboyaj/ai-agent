from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function
import os
import sys
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

def main():
    for _ in range(4):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )

        if response.candidates:
            for candidate in response.candidates:
                if not candidate.content:
                    continue
                messages.append(candidate.content)

        if not response.usage_metadata:
            raise RuntimeError("API key not found / invalid")

        function_responses = []
        if response.function_calls:
            for function_call in response.function_calls:
                function_call_result = call_function(function_call, args.verbose)
                if not function_call_result.parts:
                    raise Exception(f"Invalid function call result for {function_call.name}.")
                if not function_call_result.parts[0].function_response:
                    raise Exception(f"Invalid function call result for {function_call.name}.")
                if not function_call_result.parts[0].function_response.response:
                    raise Exception(f"Invalid function call result for {function_call.name}.")

                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                function_responses.append(function_call_result.parts[0])
            messages.append(types.Content(role="user", parts=function_responses))

        else:
            if args.verbose:
                print(f"User prompt: {args.user_prompt}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            print(response.text)
            return
    print("Error: Failed to complete task.")
    sys.exit(1)

if __name__ == "__main__":
    main()
    