"""
Embedding 模块 — 负责人: Shi Li

功能：
  将 Document.page_content 和查询字符串编码为语义向量
  使用 sentence-transformers 库加载预训练模型

候选模型：
  - all-MiniLM-L6-v2:     维度 384，轻量基线
  - BAAI/bge-base-en-v1.5: 维度 768，推荐主方案

注意：
  bge 系列模型要求 query 端加前缀 "Represent this sentence: "
  document 端不加前缀。漏加会导致检索质量严重下降。
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """语义向量编码器"""

    # bge 系列模型需要给 query 加的前缀
    BGE_QUERY_PREFIX = "Represent this sentence: "

    # 已知的 bge 模型名（用于自动判断是否加前缀）
    BGE_MODEL_KEYWORDS = ["bge-"]

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        """
        加载 sentence-transformers 模型

        Args:
            model_name: HuggingFace 模型名称
        """
        print(f"[Embedder] 加载模型: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.is_bge = any(kw in model_name.lower() for kw in self.BGE_MODEL_KEYWORDS)

        print(f"[Embedder] 模型加载完成, 维度: {self.embedding_dim}, BGE前缀: {self.is_bge}")

    def embed_documents(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """
        批量编码文档文本

        Args:
            texts: 文档文本列表
            batch_size: 编码批大小

        Returns:
            np.ndarray, shape=(n, embedding_dim)
        """
        # 文档端不加前缀
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True  # L2归一化，配合 IndexFlatIP 使用余弦相似度
        )
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        编码单条查询

        注意: bge 系列模型需要加前缀

        Args:
            query: 查询文本 (即 rewritten_query)

        Returns:
            np.ndarray, shape=(1, embedding_dim)
        """
        # bge 模型 query 端需要加前缀
        if self.is_bge:
            query = self.BGE_QUERY_PREFIX + query

        embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )
        return np.array(embedding, dtype=np.float32)
