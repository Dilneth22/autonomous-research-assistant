from src.utils.text import chunk_text
def test_chunking():
    txt = "a"*1200
    chunks = chunk_text(txt, chunk_size=500, chunk_overlap=100)
    assert len(chunks) >= 2
