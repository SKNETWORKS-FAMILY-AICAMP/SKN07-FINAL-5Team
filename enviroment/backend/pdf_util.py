import fitz  # PyMuPDF
from typing import Optional

def extract_text_from_pdf(pdf_bytes) -> Optional[str]:
    """PDF byte stream에서 텍스트 추출"""
    try:
        with fitz.open(stream=pdf_bytes.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text.strip()
    except Exception as e:
        print("PDF 파싱 오류:", e)
        return None


