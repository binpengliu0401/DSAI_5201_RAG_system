import pandas as pd
from langchain_core.documents import Document


def load_paper_parquet(parquet_path: str) -> pd.DataFrame:
    """
    读取 ai_math_paper_list 的 parquet 文件

    Args:
        parquet_path: parquet 文件路径

    Returns:
        pd.DataFrame: 原始数据
    """
    df = pd.read_parquet(parquet_path)
    print(f"[DatasetLoader] 加载完成，共 {len(df)} 篇论文")
    print(f"[DatasetLoader] 字段: {list(df.columns)}")
    return df


def extract_documents(df: pd.DataFrame) -> list[Document]:
    """
    从论文数据中提取 Document 列表

    每篇论文 = 一个 Document:
      - page_content: 论文的 abstract（摘要）
      - metadata["source"]: 论文标题
      - metadata["authors"]: 作者列表

    Args:
        df: load_paper_parquet 的输出

    Returns:
        List[Document]: 文档列表
    """
    documents = []
    skipped = 0

    for idx, row in df.iterrows():
        title = row.get("title", "")
        abstract = row.get("abstract", "")

        # 跳过没有 abstract 的论文
        if not abstract or not str(abstract).strip():
            skipped += 1
            continue

        # 获取作者列表
        authors = row.get("authors", [])
        if authors is None:
            authors = []

        doc = Document(
            page_content=str(abstract).strip(),
            metadata={
                "source": str(title).strip(),
                "authors": list(authors) if hasattr(authors, '__iter__') else []
            }
        )
        documents.append(doc)

    print(f"[DatasetLoader] 提取完成: {len(df)} 篇论文 → {len(documents)} 个 Document (跳过 {skipped} 篇无摘要)")
    return documents


# ========== 便捷入口 ==========

def load_and_process(parquet_path: str) -> list[Document]:
    """
    一键加载 + 处理: parquet → List[Document]

    Args:
        parquet_path: parquet 文件路径

    Returns:
        List[Document]: 文档列表，可直接用于 Embedding
    """
    df = load_paper_parquet(parquet_path)
    documents = extract_documents(df)
    return documents


if __name__ == "__main__":
    # 测试用: python -m app.data_processing.dataset_loader
    import sys

    parquet_path = sys.argv[1] if len(sys.argv) > 1 else "data/train-00000-of-00001.parquet"

    docs = load_and_process(parquet_path=parquet_path)

    # 打印前 3 个 Document 看看效果
    print("\n===== 前 3 个 Document 示例 =====")
    for i, doc in enumerate(docs[:3]):
        print(f"\n[{i}] source: {doc.metadata['source']}")
        print(f"    authors: {doc.metadata['authors'][:3]}...")
        print(f"    content: {doc.page_content[:200]}...")
