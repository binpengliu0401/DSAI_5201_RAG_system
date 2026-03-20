"""
向量数据库模块 — 负责人: Shi Li

功能：
  1. 构建 FAISS 索引 (支持 Flat 和 HNSW 两种)
  2. 持久化存储与加载
  3. 检索并返回 List[Document]

索引方案：
  - Flat (IndexFlatIP):  精确内积检索，小数据集首选
  - HNSW (IndexHNSWFlat): 近似检索，大数据集更快

注意：
  Embedding 已做 L2 归一化，所以 IndexFlatIP 的内积等价于余弦相似度
"""

import pickle
from pathlib import Path

import faiss
import numpy as np
from langchain_core.documents import Document


class VectorStore:
    """FAISS 向量索引管理器"""

    def __init__(self, embedding_dim: int = 768, index_type: str = "flat"):
        """
        Args:
            embedding_dim: 向量维度 (需与 Embedder 一致)
            index_type: "flat" (IndexFlatIP) 或 "hnsw" (IndexHNSWFlat)
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index: faiss.Index = None
        self.documents: list[Document] = []  # 与索引一一对应的 Document 列表

        self._build_empty_index()

    def _build_empty_index(self):
        """创建空的 FAISS 索引"""
        if self.index_type == "flat":
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        elif self.index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(self.embedding_dim, 32)  # M=32
            self.index.hnsw.efSearch = 64   # 检索时的搜索范围
            self.index.hnsw.efConstruction = 200  # 构建时的精度
        else:
            raise ValueError(f"不支持的索引类型: {self.index_type}，请使用 'flat' 或 'hnsw'")

    def build_index(self, embeddings: np.ndarray, documents: list[Document]) -> None:
        """
        构建 FAISS 索引

        Args:
            embeddings: shape=(n, embedding_dim)，已 L2 归一化
            documents: 与 embeddings 一一对应的 Document 列表
        """
        assert len(embeddings) == len(documents), \
            f"embeddings ({len(embeddings)}) 和 documents ({len(documents)}) 数量不一致"
        assert embeddings.shape[1] == self.embedding_dim, \
            f"向量维度不匹配: 期望 {self.embedding_dim}, 实际 {embeddings.shape[1]}"

        self._build_empty_index()
        self.index.add(embeddings)
        self.documents = documents

        print(f"[VectorStore] 索引构建完成: {self.index.ntotal} 条向量, 类型={self.index_type}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[Document]:
        """
        检索并返回 Top-K Document 对象列表（按相似度降序）

        Args:
            query_embedding: shape=(1, embedding_dim)
            top_k: 返回结果数

        Returns:
            List[Document]: 检索结果，metadata 中额外包含 "score" 字段
        """
        if self.index.ntotal == 0:
            print("[VectorStore] 警告: 索引为空，返回空列表")
            return []

        # 确保 top_k 不超过索引大小
        actual_k = min(top_k, self.index.ntotal)

        # FAISS 检索
        scores, indices = self.index.search(query_embedding, actual_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS 返回 -1 表示无效结果
                continue

            doc = self.documents[idx]
            # 创建新的 Document，在 metadata 中加入检索分数
            result_doc = Document(
                page_content=doc.page_content,
                metadata={
                    **doc.metadata,
                    "score": float(score)
                }
            )
            results.append(result_doc)

        return results

    def save(self, index_path: str, docs_path: str) -> None:
        """
        持久化索引和文档列表

        Args:
            index_path: FAISS 索引文件路径，如 "data/index/faiss_flat.index"
            docs_path: Document 列表文件路径，如 "data/index/documents.pkl"
        """
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        Path(docs_path).parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, index_path)
        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)

        print(f"[VectorStore] 索引已保存: {index_path} ({self.index.ntotal} 条)")
        print(f"[VectorStore] 文档已保存: {docs_path} ({len(self.documents)} 条)")

    def load(self, index_path: str, docs_path: str) -> None:
        """
        从磁盘加载索引和文档列表

        Args:
            index_path: FAISS 索引文件路径
            docs_path: Document 列表文件路径
        """
        self.index = faiss.read_index(index_path)
        with open(docs_path, "rb") as f:
            self.documents = pickle.load(f)

        assert self.index.ntotal == len(self.documents), \
            f"索引 ({self.index.ntotal}) 和文档 ({len(self.documents)}) 数量不一致，文件可能损坏"

        print(f"[VectorStore] 索引已加载: {index_path} ({self.index.ntotal} 条)")
