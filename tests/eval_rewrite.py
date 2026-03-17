# python -m tests.eval_rewrite

import os
import numpy as np
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from app.nodes.rewriting import rewrite_query

load_dotenv()

print("⏳ Loading local embedding model (BAAI/bge-base-en-v1.5)...")
embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")


def cosine_similarity(v1: list, v2: list) -> float:
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def run_evaluation():
    print("\n🚀 Starting Quantitative Evaluation for Query Rewriting Node...\n")

    # 【优化点1】：测试用例必须包含隐式实体，不能全是代词，否则无状态 RAG 必死
    test_cases = [
        {
            "id": 1,
            "vague_query": "what parameters did they use for the optimizer in the original transformer paper?",
            "target_doc": "The original Transformer uses the Adam optimizer with beta1=0.9, beta2=0.98 and epsilon=10^-9."
        },
        {
            "id": 2,
            "vague_query": "how does the transformer prevent seeing the future?",
            "target_doc": "We modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions. This masking ensures predictions depend only on known outputs."
        },
        {
            "id": 3,
            "vague_query": "tell me the datasets used to train the GPT-3 architecture.",
            "target_doc": "Datasets for GPT-3 pretraining include filtered CommonCrawl, WebText2, Books1, Books2, and Wikipedia."
        },
        {
            "id": 4,
            "vague_query": "optimizer parameters",
            # 故意塞入假的历史失败记录，逼迫大模型反思，绕开这些词去寻找新的学术词汇
            "failed_queries": ["optimizer parameters", "Adam", "learning rate"],
            "target_doc": "The original Transformer uses the Adam optimizer with beta1=0.9, beta2=0.98 and epsilon=10^-9."
        }
    ]

    total_improvement = 0.0

    for case in test_cases:
        print(f"--- Test Case #{case['id']} ---")

        # 传入 query，如果 case 里有 failed_queries 也一并传入
        state = {"query": case["vague_query"]}
        if "failed_queries" in case:
            state["failed_queries"] = case["failed_queries"]

        result = rewrite_query(state)
        rewritten_query = result.get("rewritten_query", "")
        print(f"✨ Rewritten Query: {rewritten_query}")

        # 【优化点2】：严格遵守队友 Li 的架构契约，为 Query 加上 BGE 的专用前缀
        bge_prefix = "Represent this sentence: "
        doc_vec = embedder.embed_query(case["target_doc"])  # Document 不加
        vague_vec = embedder.embed_query(bge_prefix + case["vague_query"])  # 加上前缀
        rewritten_vec = embedder.embed_query(bge_prefix + rewritten_query)  # 加上前缀

        sim_original = cosine_similarity(vague_vec, doc_vec)
        sim_rewritten = cosine_similarity(rewritten_vec, doc_vec)

        improvement = ((sim_rewritten - sim_original) / sim_original) * 100
        total_improvement += improvement

        print(f"📊 Original Similarity:  {sim_original:.4f}")
        print(f"📈 Rewritten Similarity: {sim_rewritten:.4f}")
        print(f"🔥 Improvement:          +{improvement:.2f}%\n")

    avg_improvement = total_improvement / len(test_cases)
    print("==================================================")
    print(f"🏆 EVALUATION COMPLETE: Average Similarity Lift = +{avg_improvement:.2f}%")
    print("==================================================")


if __name__ == "__main__":
    run_evaluation()
