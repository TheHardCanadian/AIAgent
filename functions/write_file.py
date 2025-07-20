import os
from google import genai

def write_file(working_directory, file_path, content):

	abs_working = os.path.abspath(working_directory)
	abs_file = os.path.abspath(os.path.join(working_directory, file_path))

	if not abs_file.startswith(abs_working):
		return f'Error: Cannot write to "{file_path} as it is outside the working directory'
	
	if not os.path.exists(abs_file):
		try:
			new_dir = os.makedirs(os.path.dirname(abs_file))
			print(new_dir)
			print(abs_file)
		except Exception as e:
			print(f"Path_exists_module exception: {e}")

	#overwrite content
	try:
		with open(abs_file, "w") as f:
			f.write(content)
		return f'Successfully wrote to "{abs_file}" ({len(content)} characters written)'
	except Exception as e:
		return f"Error: {e}"


schema_write_file = genai.types.FunctionDeclaration(
    name="write_file",
    description = "write the specified content to the specified file, constrained to the working directory.",
    parameters=genai.types.Schema(
        type=genai.types.Type.OBJECT,
        properties={
            "file_path":genai.types.Schema(
                type=genai.types.Type.STRING,
                description="The path to the file to write to, relative to the working directory",
            ),
			"content": genai.types.Schema(
				type=genai.types.Type.STRING,
				description="The content to write to the file",
			)
        },
		required=["file_path", "content"]
    )
)