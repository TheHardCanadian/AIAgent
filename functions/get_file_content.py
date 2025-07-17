import os


def get_file_content(working_directory, file_path):
    abs_file = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(abs_file, file_path))

    print(f"working directory: {abs_file}")
    print(full_path)

    if not full_path.startswith(abs_file):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(full_path):
        return f'Error: File not found or is not a regular file: "{file_path}'

    try:
        MAX_CHARS = 10000
        truncated_message = f'[...File "{file_path}" truncated at 10000 characters]'
        with open(full_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)

        if len(file_content_string) >= 10000:
            file_content_string = file_content_string + truncated_message

        return file_content_string
    except Exception as e:
        return f"Error reading files: {e}"