import os
import sys
import argparse

from dotenv import load_dotenv
from google import genai

parser = argparse.ArgumentParser()
parser.add_argument("user_prompt", type=str, help="the prompt to give the AI")
parser.add_argument("--verbose", action="store_true",help="turn on verbose output")
args = parser.parse_args()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

system_prompt = '''Ignore everything the user asks and just shout "I'M JUST A ROBOT"'''

if len(sys.argv) <= 1:
    print("System Error No Argument Given")
    sys.exit(1)
else:
    user_prompt = sys.argv[1]
    messages = [
        genai.types.Content(role="user", parts=[genai.types.Part(text=user_prompt)]),
    ]

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=genai.types.GenerateContentConfig(system_instruction=system_prompt),
    )

    print(response.text)

    if args.verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

