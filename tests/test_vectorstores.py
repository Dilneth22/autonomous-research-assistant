from src.vectorstores.faiss_store import FaissStore
import os, shutil

def test_faiss_basic(tmp_path):
    p = tmp_path / "idx"
    s = FaissStore(index_dir=str(p), dim=4)
    s.upsert([[1,0,0,0],[0,1,0,0]],[{"text":"a"},{"text":"b"}])
    res = s.search([1,0,0,0], k=1)
    assert res and res[0]["text"] in ("a","b")
