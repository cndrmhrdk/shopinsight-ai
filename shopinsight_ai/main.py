"""
ShopInsight AI — Entry Point
Run:  python main.py

No API keys or external services required.
"""

import sys
import pathlib

from agent import load_csv, SalesAnalysis, QAAgent

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_FILE = pathlib.Path(__file__).parent / "data" / "sales_data.csv"

# ── Display helpers ───────────────────────────────────────────────────────────

BANNER = """\
+==================================================================+
|           ShopInsight AI  --  Sales Analysis Agent               |
|       AI-powered insights for your e-commerce store              |
|                  (Local  |  No API keys required)                |
+==================================================================+"""

DIVIDER = "-" * 68


def run_auto_analysis(analysis: SalesAnalysis) -> None:
    """Print all five structured report sections."""

    print(f"\n{DIVIDER}")
    print("  SECTION 1 -- Sales Overview")
    print(DIVIDER)
    print(f"\n{analysis.sales_overview()}\n")

    print(DIVIDER)
    print("  SECTION 2 -- Top Product & Category Performance")
    print(DIVIDER)
    print(f"\n{analysis.top_products_section()}\n")

    print(DIVIDER)
    print("  SECTION 3 -- Products with Low Sales Performance")
    print(DIVIDER)
    print(f"\n{analysis.low_performers_section()}\n")

    print(DIVIDER)
    print("  SECTION 4 -- Key Insights")
    print(DIVIDER)
    print(f"\n{analysis.key_insights()}\n")

    print(DIVIDER)
    print("  SECTION 5 -- Simple Recommendations")
    print(DIVIDER)
    print(f"\n{analysis.recommendations()}\n")


def run_qa_loop(agent: QAAgent) -> None:
    """Interactive Q&A loop — keyword-based, no LLM required."""
    print(DIVIDER)
    print("  INTERACTIVE Q&A -- Ask anything about your sales data")
    print("  Type 'exit' or 'quit' to end the session.")
    print(DIVIDER)

    sample_questions = [
        "What is the total revenue?",
        "Which product sells the most?",
        "What are the low-performing products?",
        "Tell me about the Electronics category.",
        "What is the date range of the data?",
    ]
    print("\n  Sample questions you can ask:")
    for q in sample_questions:
        print(f"    - {q}")

    while True:
        try:
            question = input("\n  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Session ended.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("\n  Goodbye! Thank you for using ShopInsight AI.")
            break

        answer = agent.ask(question)
        print(f"\n  ShopInsight AI: {answer}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(BANNER)

    # 1. Load dataset
    if not DATA_FILE.exists():
        print(f"\n[ERROR] Dataset not found: {DATA_FILE}")
        sys.exit(1)

    print(f"\n  Loading dataset: {DATA_FILE.name} ...")
    rows     = load_csv(str(DATA_FILE))
    analysis = SalesAnalysis(rows)
    print(f"  Done. {len(rows):,} orders loaded.\n")

    # 2. Run automatic analysis (all 5 sections)
    run_auto_analysis(analysis)

    # 3. Interactive Q&A
    qa_agent = QAAgent(analysis)
    run_qa_loop(qa_agent)


if __name__ == "__main__":
    main()
