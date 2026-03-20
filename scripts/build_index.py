import argparse
from app.services.retriever import RAGRetriever


def main():
    parser = argparse.ArgumentParser(description="构建 RAG 检索索引")
    parser.add_argument(
        "--parquet",
        type=str,
        default="data/train-00000-of-00001.parquet",
        help="论文数据 parquet 文件路径",
    )
    parser.add_argument(
        "--index-dir", type=str, default="data/index", help="索引存储目录"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="BAAI/bge-base-en-v1.5",
        help="Embedding 模型名称",
    )
    parser.add_argument(
        "--index-type",
        type=str,
        choices=["flat", "hnsw"],
        default="flat",
        help="FAISS 索引类型",
    )
    args = parser.parse_args()

    config = {
        "embedding_model": args.embedding_model,
        "index_type": args.index_type,
    }

    retriever = RAGRetriever(
        parquet_path=args.parquet, index_dir=args.index_dir, config=config
    )

    retriever.build()

    # 构建完成后做一次简单检索验证
    print("\n" + "=" * 60)
    print("验证检索功能...")
    print("=" * 60)

    test_queries = [
        "chain of thought prompting reasoning",
        "large language model mathematical proof",
        "reinforcement learning reward optimization",
    ]

    for q in test_queries:
        results = retriever.retrieve(q, top_k=3)
        print(f"\nQuery: '{q}'")
        for i, doc in enumerate(results):
            print(
                f"  [{i+1}] {doc.metadata['source'][:60]:60s} | score={doc.metadata.get('score', 0):.4f}"
            )


if __name__ == "__main__":
    main()
