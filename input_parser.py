from __future__ import annotations

from io import BytesIO

from docx import Document
from pypdf import PdfReader


def read_uploaded_file(uploaded_file) -> str:
    content = uploaded_file.read()
    suffix = uploaded_file.name.lower().rsplit(".", 1)[-1]

    if suffix in {"txt", "md", "csv", "json"}:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("O arquivo enviado deve estar codificado em UTF-8.") from exc

    if suffix == "docx":
        document = Document(BytesIO(content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
        if not text.strip():
            raise ValueError("Não foi possível extrair texto do arquivo Word enviado.")
        return text

    if suffix == "pdf":
        reader = PdfReader(BytesIO(content))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
        text = "\n".join(text_parts)
        if not text.strip():
            raise ValueError(
                "Não foi possível extrair texto do PDF enviado. Se o arquivo for escaneado como imagem, será necessário OCR."
            )
        return text

    raise ValueError("Formato de arquivo não suportado.")
