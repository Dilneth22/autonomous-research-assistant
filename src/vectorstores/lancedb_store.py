import os
from typing import List, Dict, Any, Optional
import lancedb

class LanceDBStore:
    def __init__(self, index_dir: str = "./indexes", name: str = "main", dim: int = 768):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.db = lancedb.connect(index_dir)
        self.name = name
        self.dim = dim
        if self.name not in [t.name for t in self.db.table_names()]:
            self.table = self.db.create_table(self.name, data=[
                {"vector": [0.0]*self.dim, "title": "", "url": "", "text": ""}
            ])
            self.table.delete("title == ''")  # remove placeholder
        else:
            self.table = self.db.open_table(self.name)

    def upsert(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]) -> None:
        rows = []
        for vec, meta in zip(embeddings, metadatas):
            rows.append({
                "vector": vec,
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "text": meta.get("text", ""),
                "published_at": meta.get("published_at", ""),
            })
        if rows:
            self.table.add(rows)

    def search(self, query_emb: List[float], k: int = 8, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        q = self.table.search(query_emb).limit(k)
        if where:
            # Simple equality filters
            for key, val in where.items():
                q = q.where(f"{key} == '{val}'")
        return [dict(r) for r in q.to_list()]

    def stats(self) -> Dict[str, Any]:
        return {"count": self.table.count_rows(), "path": self.index_dir, "table": self.name}
