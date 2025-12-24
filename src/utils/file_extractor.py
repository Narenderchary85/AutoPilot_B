import fitz  # pymupdf
import pandas as pd
from docx import Document
from fastapi import UploadFile
import io

SUPPORTED_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
]


async def extract_text_from_file(file: UploadFile) -> str:
    if file.content_type not in SUPPORTED_TYPES:
        raise ValueError("Unsupported file type")

    if file.content_type == "application/pdf":
        return await extract_pdf(file)

    if file.content_type.endswith("wordprocessingml.document"):
        return await extract_docx(file)

    if file.content_type == "text/plain":
        return await extract_txt(file)

    if file.content_type == "text/csv":
        return await extract_csv(file)

    if file.content_type.endswith("spreadsheetml.sheet"):
        return await extract_xlsx(file)

    return ""


async def extract_pdf(file: UploadFile) -> str:
    content = await file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    text = []
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)


async def extract_docx(file: UploadFile) -> str:
    content = await file.read()
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)


async def extract_txt(file: UploadFile) -> str:
    return (await file.read()).decode("utf-8", errors="ignore")


async def extract_csv(file: UploadFile) -> str:
    df = pd.read_csv(io.BytesIO(await file.read()))
    return df.to_string(index=False)


async def extract_xlsx(file: UploadFile) -> str:
    df = pd.read_excel(io.BytesIO(await file.read()))
    return df.to_string(index=False)
