import os
import subprocess
from google import genai

def run_python_file(working_directory, file_path, args=[]):
    abs_working = os.path.abspath(working_directory)
    abs_file = os.path.abspath(os.path.join(abs_working, file_path))

    if not abs_file.startswith(abs_working):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(abs_file):
        return f'Error: File "{file_path}" not found.'

    if not abs_file.endswith(".py"):
        return f'Error: "{file_path}"    is not a Python file.'

    try:

        command = ["python", abs_file] + args

        result = subprocess.run(command, timeout = 30, capture_output = True, cwd=abs_working, text=True)
        output = f"STDOUT: {result.stdout}"
        error = f"STDERR: {result.stderr}"

        if result.returncode != 0:
            output = f"{output} Process exited with code {result.returncode}"



        combined_output = output + "\n" + error
        if result.stdout == "" and result.stderr == "":
            return "No output produced"

        return combined_output


    except Exception as e:
        return f"Error: executing Python file: {e}"




schema_run_python_file = genai.types.FunctionDeclaration(
    name="run_python_file",
    description = "run the specified python file, constrained to the working directory.",
    parameters=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        properties={
            "file_path":genai.types.Schema(
                type=genai.types.Type.STRING,
                description="run the specified python file, as long as it is in the working directory.",
            ),
            "args":genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(type=genai.types.Type.STRING),
                description="Optional command line arguments to pass to the Python file.",
            )
        },
        required=["file_path"]
    )
)
