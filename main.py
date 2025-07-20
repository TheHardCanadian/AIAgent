import os
import sys
import argparse
import json
from dotenv import load_dotenv
from google import genai
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file



def call_function(function_call_part, verbose=False):
    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    function_name = function_call_part.name

    if verbose:
        print(f"Calling function {function_name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return genai.types.Content(
            role="tool",
            parts=[
                genai.types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"
    function_result = function_map[function_name](**args)
    return genai.types.Content(
        role="tool",
        parts=[
            genai.types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


available_functions = genai.types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("user_prompt", type=str, help="the prompt to give the AI")
    parser.add_argument("--verbose", action="store_true",help="turn on verbose output")
    args = parser.parse_args()


    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """
    You are a helpful AI coding agent.
    
    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:
    
    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files
    
    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

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
            config=genai.types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt),
        )

        if args.verbose:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        if not response.function_calls:
            raise Exception("no function responses generated, exiting.")

        function_responses = []
        for function_call_part in response.function_calls:
            function_call_result = call_function(function_call_part, args.verbose)
            if (
                    not function_call_result.parts
                    or not function_call_result.parts[0].function_response
            ):
                raise Exception("empty function call result")
            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
            function_responses.append(function_call_result.parts[0])



        if args.verbose:
            print(f"User prompt: {user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            print(f"-> {function_call_result.parts[0].function_response.response}")

if __name__ == "__main__":
    main()