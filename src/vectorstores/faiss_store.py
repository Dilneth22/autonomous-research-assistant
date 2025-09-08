import os, json
from typing import List, Dict, Any, Optional
import numpy as np
import faiss

class FaissStore:
    def __init__(self, index_dir: str = "./indexes", dim: int = 768, name: str = "main"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.dim = dim
        self.name = name
        self.index_path = os.path.join(index_dir, f"{name}.faiss")
        self.meta_path = os.path.join(index_dir, f"{name}.meta.jsonl")
        self._index = None
        self._count = 0
        self._load()

    def _load(self):
        if os.path.exists(self.index_path):
            self._index = faiss.read_index(self.index_path)
            # Count from meta file
            if os.path.exists(self.meta_path):
                self._count = sum(1 for _ in open(self.meta_path, "r", encoding="utf-8"))
        else:
            self._index = faiss.IndexFlatL2(self.dim)
            self._count = 0

    def _persist(self):
        faiss.write_index(self._index, self.index_path)

    def upsert(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]) -> None:
        if not embeddings:
            return
        arr = np.array(embeddings, dtype="float32")
        if arr.shape[1] != self.dim:
            # Try to auto-fix dimension by padding/truncation:
            dim = arr.shape[1]
            if dim < self.dim:
                pad = np.zeros((arr.shape[0], self.dim - dim), dtype="float32")
                arr = np.concatenate([arr, pad], axis=1)
            else:
                arr = arr[:, : self.dim]
        self._index.add(arr)
        with open(self.meta_path, "a", encoding="utf-8") as f:
            for m in metadatas:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        self._count += len(embeddings)
        self._persist()

    def _iter_meta(self):
        if not os.path.exists(self.meta_path):
            return []
        with open(self.meta_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def search(self, query_emb: List[float], k: int = 8, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        import numpy as np
        if self._count == 0:
            return []
        q = np.array([query_emb], dtype="float32")
        if q.shape[1] != self.dim:
            dim = q.shape[1]
            if dim < self.dim:
                pad = np.zeros((1, self.dim - dim), dtype="float32")
                q = np.concatenate([q, pad], axis=1)
            else:
                q = q[:, : self.dim]
        D, I = self._index.search(q, min(k, self._count))
        metas = self._iter_meta()
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx < 0 or idx >= len(metas):
                continue
            m = metas[idx]
            m["_distance"] = float(dist)
            results.append(m)
        # Simple metadata filter
        if where:
            def match(meta):
                return all(meta.get(k) == v for k, v in where.items())
            results = [r for r in results if match(r)]
        return results

    def stats(self) -> Dict[str, Any]:
        return {"count": self._count, "dim": self.dim, "path": self.index_path}
