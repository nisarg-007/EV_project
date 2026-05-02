"""
Demo script — runs curated queries through the full agent pipeline.
Use this during live demonstrations and presentations.
"""

DEMO_QUERIES = [
    "How many electric vehicles are registered in King County?",
    "What are the top 5 most popular EV makes in Washington state?",
    "What is the CAFV eligibility breakdown across all registered vehicles?",
    "What EV incentives are available in Washington state?",
    "Compare EV adoption trends: which model years saw the fastest growth?",
    "What does Washington law say about EV charging station requirements?",
    "Which utility providers serve the most EV owners in Washington?",
    "Is a 2024 Tesla Model Y eligible for any state-level tax credits?",
]

if __name__ == "__main__":
    try:
        from scripts.agent_workflow import run_agent
    except ImportError:
        print("❌ agent_workflow.py not available yet.")
        print("   Run this script after Person 4 has pushed their code.")
        exit(1)
    
    print("=" * 70)
    print("  ⚡ EV INTELLIGENCE PLATFORM — LIVE DEMO")
    print("=" * 70)
    
    for i, query in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'─' * 60}")
        print(f"  🔍 Demo Query {i}/{len(DEMO_QUERIES)}")
        print(f"  Q: {query}")
        print(f"{'─' * 60}")
        
        try:
            answer = run_agent(query)
            print(f"\n  💬 Answer:\n  {answer}\n")
        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")
    
    print("=" * 70)
    print("  ✅ Demo complete.")
    print("=" * 70)
