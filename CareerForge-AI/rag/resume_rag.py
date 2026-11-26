import io
import re
from pathlib import Path


def extract_resume(uploaded_file) -> str:
    """Extract text from a Streamlit uploaded PDF, DOCX, or TXT file."""
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()
    if name.endswith('.pdf'):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith('.docx'):
        from docx import Document
        document = Document(io.BytesIO(data))
        text = "\n".join(p.text for p in document.paragraphs)
        for table in document.tables:
            for row in table.rows:
                text += "\n" + " | ".join(cell.text for cell in row.cells)
    elif name.endswith('.txt'):
        text = data.decode('utf-8', errors='ignore')
    else:
        raise ValueError('Please upload a PDF, DOCX, or TXT resume.')
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        raise ValueError('Could not extract readable text. Try a text-based PDF or DOCX file.')
    return text


def chunk_text(text: str, chunk_size: int = 850, overlap: int = 150) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + chunk_size])
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(words):
            break
    return chunks


def retrieve_resume_context(resume_text: str, query: str, top_k: int = 4) -> str:
    """Local TF-IDF retrieval: no embedding API or vector database key required."""
    chunks = chunk_text(resume_text)
    if not chunks:
        return ''
    if not query.strip():
        return '\n\n'.join(chunks[:top_k])
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(chunks + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        indexes = scores.argsort()[::-1][:top_k]
        selected = [chunks[i] for i in indexes if scores[i] > 0]
        if selected:
            return '\n\n'.join(selected)
    except ValueError:
        pass
    # Fallback when the resume/query contains only words outside the vectorizer vocabulary.
    return '\n\n'.join(chunks[:top_k])
