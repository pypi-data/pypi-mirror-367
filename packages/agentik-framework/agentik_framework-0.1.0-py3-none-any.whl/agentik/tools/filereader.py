# agentik/tools/filereader.py

"""
Tool: FileReaderTool
Reads and returns the content of a text file (.txt or .md) with fallback encoding handling.
"""

from pathlib import Path
from agentik.tools.base import Tool

class FileReaderTool(Tool):
    name = "filereader"
    description = "Read text content from a .txt or .md file."

    def run(self, input_text: str) -> str:
        """
        Reads a file path passed after the 'filereader' keyword and returns its contents.
        Attempts multiple encodings for compatibility.
        """
        filepath = input_text.replace(self.name, "", 1).strip()
        if not filepath:
            return "[FileReaderTool] No file path provided."

        try:
            path = Path(filepath)
            if not path.exists():
                return f"[FileReaderTool] File not found: {filepath}"

            for encoding in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    return path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue

            return "[FileReaderTool Error]: Unable to decode file."

        except Exception as e:
            return f"[FileReaderTool Error]: {str(e)}"
