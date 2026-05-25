from google.genai import types 
import os
import subprocess

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python file relative to the working directory and returns the output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to run the python script from",
            ),
            "arguments": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional arguments to pass to the python script",
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # Verify target path is within the working directory
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not target_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        command = ['python3', target_path]

        # Add arguments if provided
        if args:
            command.extend(args)

        # Run the command
        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = ""
        if result.returncode != 0:
            output = f"Process exited with code {result.returncode}\n"
        
        elif not result.stdout and not result.stderr:
            output = "No output produced."
        
        else:
            output = f"STDOUT:\n{result.stdout}"
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

        return output
       
    except Exception as e:
        return f"Error: executing Python file: {e}"
