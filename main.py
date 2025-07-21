import os
import sys
import argparse
import json
from dotenv import load_dotenv
from google import genai
from call_functions import available_functions, call_function

def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("user_prompt", type=str, help="the prompt to give the AI")
    parser.add_argument("--verbose", action="store_true",help="turn on verbose output")
    args = parser.parse_args()


    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    verbose = args.verbose

    system_prompt = """
You are a helpful AI coding agent working in a calculator project directory.

When a user asks a question, you should explore the codebase using the available functions to understand how it works before providing an answer.

Available operations:
- List files and directories to understand the project structure
- Read file contents to analyze the code
- Execute Python files with optional arguments to test functionality
- Write or overwrite files when needed

Always start by exploring the project structure with get_files_info, then read relevant files with get_file_content to understand the codebase before answering questions.

All paths should be relative to the working directory.
"""

    if len(sys.argv) <= 1:
        print("System Error No Argument Given")
        sys.exit(1)
    else:
        user_prompt = sys.argv[1]
        messages = [
            genai.types.Content(role="user", parts=[genai.types.Part(text=user_prompt)]),
        ]

        content_count = 0
        while True:
            content_count += 1
            if content_count > 20:
                print(f"Maximum iterations reached")
                sys.exit(1)
            try:
                final_response = generate_content(client, messages, verbose, system_prompt)
                if final_response:
                    print(f"Final response:\n{final_response}")
                    break
            except Exception as e:
                print(f"Error generating content: {e}")


def generate_content(client, messages, verbose, system_prompt):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=genai.types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
    )
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.candidates:
        for candidate in response.candidates:
            function_call_content = candidate.content
            messages.append(function_call_content)

    if not response.function_calls:
        return response.text

    function_responses = []
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose)
        if (
                not function_call_result.parts
                or not function_call_result.parts[0].function_response
        ):
            raise Exception("empty function call result")
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
        function_responses.append(function_call_result.parts[0])

    if not function_responses:
        raise Exception("no function responses generated, exiting.")

    messages.append(genai.types.Content(parts=function_responses, role="tool"))
    return None


if __name__ == "__main__":
    main()