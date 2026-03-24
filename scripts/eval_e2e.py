# Owner: Liu
# Responsibility: End-to-End quantitative evaluation
# Output: success rate, avg latency, node latency breakdown, retry score improvement

import json
import time
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from main import run_workflow

# 25 Test Questions
QUESTIONS = [
    # High Quality
    {"id": 1, "category": "high", "question": "What is chain of thought prompting?"},
    {
        "id": 2,
        "category": "high",
        "question": "How does RLHF work in large language models?",
    },
    {
        "id": 3,
        "category": "high",
        "question": "What is retrieval-augmented generation?",
    },
    {
        "id": 4,
        "category": "high",
        "question": "How does the attention mechanism work in Transformers?",
    },
    {
        "id": 5,
        "category": "high",
        "question": "What is the difference between zero-shot and few-shot prompting?",
    },
    {"id": 6, "category": "high", "question": "What is instruction tuning?"},
    {
        "id": 7,
        "category": "high",
        "question": "How do decoder-only language models generate text?",
    },
    {"id": 8, "category": "high", "question": "What is the GSM8K benchmark used for?"},
    # Medium Quality
    {
        "id": 9,
        "category": "medium",
        "question": "How do LLMs handle mathematical reasoning?",
    },
    {
        "id": 10,
        "category": "medium",
        "question": "What makes some prompting strategies better than others?",
    },
    {
        "id": 11,
        "category": "medium",
        "question": "How is retrieval used to reduce hallucination?",
    },
    {
        "id": 12,
        "category": "medium",
        "question": "Why do larger models tend to perform better?",
    },
    {
        "id": 13,
        "category": "medium",
        "question": "What role does fine-tuning play after pretraining?",
    },
    {
        "id": 14,
        "category": "medium",
        "question": "How do models learn to follow human instructions?",
    },
    {
        "id": 15,
        "category": "medium",
        "question": "What are the limitations of dense retrieval?",
    },
    {
        "id": 16,
        "category": "medium",
        "question": "How does self-consistency improve reasoning?",
    },
    # Low Quality
    {
        "id": 17,
        "category": "low",
        "question": "How do chain of thought and retrieval work together to improve accuracy?",
    },
    {
        "id": 18,
        "category": "low",
        "question": "What are the tradeoffs between model size, training cost, and performance?",
    },
    {
        "id": 19,
        "category": "low",
        "question": "How do positional encodings affect long-context reasoning?",
    },
    {
        "id": 20,
        "category": "low",
        "question": "How do symbolic and neural approaches to math solving compare?",
    },
    # Noise
    {
        "id": 21,
        "category": "noise",
        "question": "What is the best recipe for making pasta carbonara?",
    },
    {
        "id": 22,
        "category": "noise",
        "question": "What does the fox say about mathematics?",
    },
    {"id": 23, "category": "noise", "question": "Who won the FIFA World Cup in 2022?"},
    {"id": 24, "category": "noise", "question": "asdfjkl qwerty transformer?"},
    {
        "id": 25,
        "category": "noise",
        "question": "How does climate change affect transformer architecture?",
    },
]

HALLUCINATION_THRESHOLD = 0.7


# Run Evaluation
def run_evaluation():
    results = []

    for i, item in enumerate(QUESTIONS):
        qid = item["id"]
        category = item["category"]
        question = item["question"]

        print(f"\n[{i+1:02d}/25] (category={category}) {question[:70]}")

        try:
            start = time.time()
            state = run_workflow(question)
            elapsed = round((time.time() - start) * 1000, 2)

            trace = state.get("execution_trace", [])
            score = state.get("hallucination_score", 0.0)
            retries = state.get("retry_count", 0)
            decision = state.get("final_decision", "")

            # node latency: sum per node name across all trace entries
            node_latencies = defaultdict(float)
            for entry in trace:
                node_latencies[entry["node"]] += entry["latency_ms"]

            # retry score progression: collect grading scores in order
            grading_scores = [
                entry["key_output"]["hallucination_score"]
                for entry in trace
                if entry["node"] == "grading"
                and "hallucination_score" in entry.get("key_output", {})
            ]

            results.append(
                {
                    "id": qid,
                    "category": category,
                    "question": question,
                    "final_score": score,
                    "retry_count": retries,
                    "decision": decision,
                    "success": score >= HALLUCINATION_THRESHOLD,
                    "e2e_latency_ms": elapsed,
                    "node_latencies": dict(node_latencies),
                    "grading_scores": grading_scores,
                }
            )

            print(
                f"    score={score:.3f}  retries={retries}  decision={decision}  e2e={elapsed:.0f}ms"
            )

        except Exception as e:
            print(f"    ERROR: {e}")
            results.append(
                {
                    "id": qid,
                    "category": category,
                    "question": question,
                    "final_score": 0.0,
                    "retry_count": 0,
                    "decision": "error",
                    "success": False,
                    "e2e_latency_ms": 0.0,
                    "node_latencies": {},
                    "grading_scores": [],
                }
            )

    return results


# Analysis
def analyze(results):
    total = len(results)
    success = sum(1 for r in results if r["success"])

    print("\n" + "═" * 60)
    print("  END-TO-END EVALUATION REPORT")
    print("═" * 60)

    # 1. Overall success rate
    print(f"\n[1] Overall Success Rate: {success}/{total} = {success/total*100:.1f}%")

    # 2. Success rate by category
    print("\n[2] Success Rate by Category:")
    for cat in ["high", "medium", "low", "noise"]:
        cat_results = [r for r in results if r["category"] == cat]
        cat_success = sum(1 for r in cat_results if r["success"])
        print(
            f"    {cat:<8}: {cat_success}/{len(cat_results)} = {cat_success/len(cat_results)*100:.1f}%"
        )

    # 3. Avg end-to-end latency
    valid = [r for r in results if r["e2e_latency_ms"] > 0]
    avg_e2e = np.mean([r["e2e_latency_ms"] for r in valid])
    print(f"\n[3] Avg End-to-End Latency: {avg_e2e/1000:.2f}s  ({avg_e2e:.0f}ms)")

    # 4. Node latency breakdown
    node_totals = defaultdict(list)
    node_order = ["rewriting", "retrieval", "generation", "grading", "router"]
    for r in valid:
        for node, lat in r["node_latencies"].items():
            node_totals[node].append(lat)

    print("\n[4] Avg Node Latency Breakdown:")
    for node in node_order:
        if node in node_totals:
            avg = np.mean(node_totals[node])
            print(f"    {node:<12}: {avg/1000:.2f}s  ({avg:.0f}ms)")

    # 5. Retry analysis
    retried = [r for r in results if r["retry_count"] > 0]
    no_retry = [r for r in results if r["retry_count"] == 0]
    print(f"\n[5] Retry Analysis:")
    print(f"    Samples with retry:    {len(retried)}/{total}")
    print(f"    Samples without retry: {len(no_retry)}/{total}")

    if retried:
        improvements = []
        for r in retried:
            scores = r["grading_scores"]
            if len(scores) >= 2:
                improvement = scores[-1] - scores[0]
                improvements.append(improvement)
                print(
                    f"    Q{r['id']:02d} scores: {[round(s,3) for s in scores]}  improvement={improvement:+.3f}"
                )
        if improvements:
            avg_imp = np.mean(improvements)
            print(f"    Avg score improvement after retry: {avg_imp:+.3f}")

    return node_totals, node_order


# Plot
def plot_node_latency(
    node_totals, node_order, output_path="scripts/eval_node_latency.png"
):
    nodes = [n for n in node_order if n in node_totals]
    avgs = [np.mean(node_totals[n]) / 1000 for n in nodes]  # convert to seconds

    colors = {
        "rewriting": "#4CAF50",
        "retrieval": "#2196F3",
        "generation": "#9C27B0",
        "grading": "#FF9800",
        "router": "#9E9E9E",
    }

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(
        nodes, avgs, color=[colors.get(n, "#607D8B") for n in nodes], width=0.5
    )

    for bar, val in zip(bars, avgs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{val:.2f}s",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_title("MathMind-RAG — Average Node Latency", fontsize=13, fontweight="bold")
    ax.set_xlabel("Node")
    ax.set_ylabel("Avg Latency (s)")
    ax.set_ylim(0, max(avgs) * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"\n[Chart] Saved to {output_path}")
    plt.show()


def plot_score_by_category(results, output_path="scripts/eval_score_by_category.png"):
    categories = ["high", "medium", "low", "noise"]
    cat_colors = {
        "high": "#4CAF50",
        "medium": "#2196F3",
        "low": "#FF9800",
        "noise": "#F44336",
    }

    fig, ax = plt.subplots(figsize=(10, 5))

    x = 0
    xticks, xlabels = [], []

    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        for r in cat_results:
            color = cat_colors[cat]
            ax.bar(x, r["final_score"], color=color, width=0.7, alpha=0.85)
            xticks.append(x)
            xlabels.append(f"Q{r['id']}")
            x += 1
        x += 0.5

    ax.axhline(
        y=HALLUCINATION_THRESHOLD,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label=f"Threshold ({HALLUCINATION_THRESHOLD})",
    )
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, fontsize=7, rotation=45)
    ax.set_ylabel("Hallucination Score")
    ax.set_title(
        "MathMind-RAG — Final Score per Question", fontsize=13, fontweight="bold"
    )
    ax.set_ylim(0, 1.1)

    patches = [mpatches.Patch(color=cat_colors[c], label=c) for c in categories]
    patches.append(plt.Line2D([0], [0], color="red", linestyle="--", label=f"Threshold {HALLUCINATION_THRESHOLD}"))  # type: ignore
    ax.legend(handles=patches, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"[Chart] Saved to {output_path}")
    plt.show()


# Save raw results
def save_results(results, path="scripts/eval_results.json"):
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[Data] Raw results saved to {path}")


if __name__ == "__main__":
    import sys

    strategy = sys.argv[1] if len(sys.argv) > 1 else "default"
    results = run_evaluation()
    node_totals, node_order = analyze(results)
    plot_node_latency(
        node_totals, node_order, output_path=f"scripts/eval_node_latency_{strategy}.png"
    )
    plot_score_by_category(results, output_path=f"scripts/eval_score_{strategy}.png")
    save_results(results, path=f"scripts/eval_results_{strategy}.json")
