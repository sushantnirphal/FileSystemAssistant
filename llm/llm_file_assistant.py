import os
import json
from pyexpat.errors import messages
from dotenv import load_dotenv
from openai import OpenAI

from tools.fs_tools import (
    read_file,
    list_files,
    write_file,
    search_in_file
)

# Load environment variables
load_dotenv()

# Create Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": """
            List files from a directory.

            Resume files are stored in:
            data/resumes/

            Example:
            directory = "data/resumes"
            extension = ".docx, .pdf, .txt"
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path"
                    },
                    "extension": {
                        "type": "string",
                        "description": "Optional file extension filter like .pdf or .txt"
                    }
                },
                "required": ["directory"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": """
            Read a resume file.

            Resume files are stored in:
            data/resumes/

            Example paths:
            data/resumes/resume_john_doe.txt
            data/resumes/resume_jane_smith.pdf
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path of the file to read"
                    }
                },
                "required": ["filepath"]
            }
        }
    }
]

# Tool map
tool_map = {
    "read_file": read_file,
    "list_files": list_files,
    "write_file": write_file,
    "search_in_file": search_in_file
}


def ask_llm(user_query):

    messages = [
        {
            "role": "system",
            "content": """
            You are an AI File Assistant.

            Resume files are located in:
            data/resumes/

            Rules:
            1. Always use valid JSON when calling tools.
            2. Use complete file paths.
            3. Never generate invalid JSON.
            4. Use available tools whenever required.
            """
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS
            # tool_choice="auto"
        )

        message = response.choices[0].message

        print("DEBUG:", message)

        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                function_name = tool_call.function.name

                try:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError:
                    return "Model generated invalid JSON."

                if function_name not in tool_map:
                    return f"Unknown tool: {function_name}"

                result = tool_map[function_name](**arguments)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    }
                )
            print("\nMessages sent to final LLM:\n")
            for msg in messages:
                print(msg)

            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )

            return final_response.choices[0].message.content

        return message.content

    except Exception as e:
        return f"Error: {str(e)}"