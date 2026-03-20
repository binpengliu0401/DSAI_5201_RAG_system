from pathlib import Path
from langchain_core.documents import Document

from app.dataset_processing.dataset_loader import load_and_process
from app.dataset_processing.embedder import Embedder
from app.dataset_processing.vector_store import VectorStore


class RAGRetriever:

    DEFAULT_CONFIG = {
        "embedding_model": "BAAI/bge-base-en-v1.5",
        "index_type": "flat",
        "top_k": 5,
    }

    def __init__(
        self, parquet_path: str, index_dir: str = "data/index", config: dict = None  # type: ignore
    ):
        self.parquet_path = parquet_path
        self.index_dir = Path(index_dir)
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        self.embedder: Embedder = None  # type: ignore
        self.vector_store: VectorStore = None  # type: ignore

    def _get_index_paths(self) -> tuple[str, str]:
        index_type = self.config["index_type"]
        index_path = str(self.index_dir / f"faiss_{index_type}.index")
        docs_path = str(self.index_dir / "documents.pkl")
        return index_path, docs_path

    def _init_embedder(self):
        if self.embedder is None:
            self.embedder = Embedder(model_name=self.config["embedding_model"])

    def build(self) -> None:
        print("=" * 60)
        print("[RAGRetriever] Starting to build index...")
        print("=" * 60)

        print("\n[Step 1/4] Loading paper dataset...")
        documents = load_and_process(parquet_path=self.parquet_path)

        print("\n[Step 2/4] Encoding document vectors...")
        self._init_embedder()
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedder.embed_documents(texts)
        print(f"[Step 2/4] Encoding Complete:{embeddings.shape}")

        print("\n[Step 3/4] Building FAISS index...")
        self.vector_store = VectorStore(
            embedding_dim=self.embedder.embedding_dim,  # type: ignore
            index_type=self.config["index_type"],
        )
        self.vector_store.build_index(embeddings, documents)

        print("\n[Step 4/4] Saving index to disk...")
        index_path, docs_path = self._get_index_paths()
        self.vector_store.save(index_path, docs_path)

        print("\n" + "=" * 60)
        print(f"[RAGRetriever] Index building complete! Total {len(documents)} papers")
        print("=" * 60)

    def load(self) -> None:
        self._init_embedder()

        index_path, docs_path = self._get_index_paths()

        if not Path(index_path).exists():
            raise FileNotFoundError(
                f"Index file does not exist: {index_path}\n"
                f"Please execute retriever.build() building Indexes"
            )

        self.vector_store = VectorStore(
            embedding_dim=self.embedder.embedding_dim,  # type: ignore
            index_type=self.config["index_type"],
        )
        self.vector_store.load(index_path, docs_path)

    def retrieve(self, query: str, top_k: int = None) -> list[Document]:  # type: ignore
        if self.vector_store is None:
            raise RuntimeError(
                "The index is uninitialized. Please call build() or load() first."
            )

        if top_k is None:
            top_k = self.config["top_k"]

        query_embedding = self.embedder.embed_query(query)

        results = self.vector_store.search(query_embedding, top_k=top_k)

        return results
