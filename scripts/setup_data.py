from pathlib import Path

PARQUET_PATH = Path("data/train-00000-of-00001.parquet")
INDEX_DIR = Path("data/index")
INDEX_FILE = INDEX_DIR / "faiss_flat.index"
DATASET_REPO = "fzyzcjy/ai_math_paper_list"


def _download_parquet():
    print("[setup] Parquet file not found, downloading from HuggingFace...")
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        raise ImportError("Run: pip install huggingface_hub")

    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    hf_hub_download(
        repo_id=DATASET_REPO,
        filename="data/train-00000-of-00001.parquet",
        repo_type="dataset",
        local_dir=".",
    )
    print(f"[setup] Downloaded to {PARQUET_PATH}")


def _build_index():
    print("[setup] FAISS index not found, building...")
    from app.services.retriever import RAGRetriever

    RAGRetriever = RAGRetriever(
        parquet_path=str(PARQUET_PATH),
        index_dir=str(INDEX_DIR),
    )
    RAGRetriever.build()
    print("[setup] Index built successfully.")


def ensure_data_ready():
    if not PARQUET_PATH.exists():
        _download_parquet()
    else:
        print(f"[setup] Parquet file found: {PARQUET_PATH}")
    if not INDEX_FILE.exists():
        _build_index()
    else:
        print(f"[setup] FAISS index found: {INDEX_FILE}")

    print("[setup] Data is ready.")


if __name__ == "__main__":
    ensure_data_ready()
