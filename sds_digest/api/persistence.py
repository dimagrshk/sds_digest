import os
from pathlib import Path

from fastapi import UploadFile


class Persistence:
    UPLOAD_BASE_DIR = Path("data/uploads")
    UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)

    def __init__(self):
        self.upload_base_dir = self.UPLOAD_BASE_DIR

    def save_uploaded_file(self, sds_id: str, file: UploadFile):
        file_path = self.upload_base_dir / sds_id / file.filename
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return file_path

    def save_extracted_markdown(self, sds_id: str, markdown: str):
        markdown_path = self.upload_base_dir / sds_id / "extracted.md"
        os.makedirs(markdown_path.parent, exist_ok=True)
        with open(markdown_path, "w") as f:
            f.write(markdown)
        return markdown_path


PERSISTENCE = Persistence()
