
# Read file fuction
from datetime import datetime

import re


from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document


def read_file(filepath: str) -> dict:
    try:
        file_path = Path(filepath)

        if not file_path.exists():
            return {
                "success": False,
                "message": f"File {filepath} does not exist."
            }

        text = ""

        if file_path.suffix == ".txt":

            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        elif file_path.suffix == ".pdf":

            reader = PdfReader(filepath)

            for page in reader.pages:
                text += page.extract_text() + "\n"

        elif file_path.suffix == ".docx":

            doc = Document(filepath)

            for para in doc.paragraphs:
                text += para.text + "\n"

        else:
            return {
                "success": False,
                "message": "Unsupported file type"
            }

        return {
            "success": True,
            "content": text,
            "metadata": {
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "extension": file_path.suffix
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

#list files 

from pathlib import Path
from datetime import datetime

def list_files(directory: str, extension: str = None) -> list:

    result = []

    try:
        directory_path = Path(directory)

        for file in directory_path.iterdir():

            if file.is_file():

                if extension and file.suffix != extension:
                    continue

                result.append({
                    "name": file.name,
                    "size": file.stat().st_size,
                    "modified_date":
                        datetime.fromtimestamp(
                            file.stat().st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S")
                })

        return result

    except Exception as e:
        return [{"error": str(e)}]
    

#Write file function 

def write_file(filepath: str, content: str) -> dict:

    try:
        path = Path()

        path.parent.mkdir(
            parents = True,
            exist_ok=True
        )

        with open(path,"w",encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,    
            "message": f"File {filepath} has been written successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred while writing the file: {str(e)}"
        }
    

# search in file function

def search_in_file(filepath:str,keyword:str)->dict:

    file_data = read_file(filepath)

    if not file_data["success"]:
        return file_data
    
    text = file_data["content"]

    matches = []

    pattern = re.compile(
        keyword,
        re.IGNORECASE
    )

    for match in pattern.finditer(text):

        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)

        context = text[start:end]
        matches.append(context)
        
    return {
        "success": True,
        "keyword": keyword,
        "count": len(matches),
        "matches": matches
    }    
