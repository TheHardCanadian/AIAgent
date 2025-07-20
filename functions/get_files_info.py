import os
from google import genai

def get_files_info(working_directory, directory="."):
    print(f"Args to join: {directory}")
    abs_working_directory = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_directory, directory))
    print(full_path)

    if not full_path.startswith(abs_working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(full_path):
        return f'Error: "{full_path}" is not a directory'

    try:
        directory_list = os.listdir(full_path)
        data_list = []

        for i in directory_list:
            filepath = os.path.join(full_path, i)
            size = os.path.getsize(filepath)
            is_dir = os.path.isdir(filepath)
            combined_string = f"- {i}: file_size={size} bytes, is_dir={is_dir}"
            data_list.append(combined_string)

        joined_string = "\n".join(data_list)
        return joined_string

    except Exception as e:
        return f"Error listing files: {e}"


schema_get_files_info = genai.types.FunctionDeclaration(
    name="get_files_info",
    description = "Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        properties={
            "directory":genai.types.Schema(
                type=genai.types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            )
        }
    )
)



