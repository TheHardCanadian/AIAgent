import os
import subprocess


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

        if result.stdout == "":
            return "No output produced"

        combined_output = output + "\n" + error
        return combined_output
    except Exception as e:
        return f"Error: executing Python file: {e}"