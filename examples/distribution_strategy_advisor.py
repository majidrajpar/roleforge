"""
Distribution Strategy Advisor

Uses RoleForge's own agent roles as an advisory board to evaluate:
"Should we share on GitHub or sell on a commercial marketplace?"

This demonstrates the library's utility for real business decisions.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crewai import LLM, Task, Crew
from loader import RoleRegistry
from models import RuntimeContext
from adapters.crewai_adapter import CrewAIAdapter


def get_advisory_board():
    """Create a multi-disciplinary advisory board from RoleForge roles."""
    
    api_key = os.getenv("OLLAMA_API_KEY", "your-api-key-here")
    
    llm = LLM(
        model="kimi-k2.7-code:cloud",
        base_url="https://ollama.com/v1",
        api_key=api_key,
    )
    
    context = RuntimeContext(llm=llm, tools=[], allow_delegation=False)
    adapter = CrewAIAdapter(context)
    
    registry = RoleRegistry()
    registry.index()
    
    # Strategic advisors for distribution decision
    board_config = [
        ("enterprise_risk_strategist", "crewai"),  # Strategic positioning
        ("governance_analyst", "crewai"),           # Legal/business structure
        ("ethics_advisor", "crewai"),               # Community obligations
        ("data_storyteller", "crewai"),             # Market positioning
    ]
    
    advisors = []
    for role_id, framework in board_config:
        role, overlay = registry.get_role_with_overlay(role_id, framework)
        agent = adapter.adapt(role, overlay.data if overlay else None)
        advisors.append(agent)
    
    return advisors


def evaluate_distribution_strategy():
    """Evaluate: GitHub vs Commercial Marketplace vs Hybrid."""
    
    advisors = get_advisory_board()
    
    context = """
We have built RoleForge: a framework-agnostic YAML library for AI agent roles with:
- 31 professional roles across 7 domains
- Multi-framework adapters (CrewAI, LangChain, LangGraph)
- Role selector with keyword + LLM matching
- 43 tests, comprehensive docs
- Currently under Elastic License 2.0

We are considering three distribution strategies:

OPTION A: GitHub (Open Source)
- Free, public repository
- Build community and contributors
- Monetize via consulting/services later
- Elastic License protects against SaaS competitors

OPTION B: Commercial Marketplace (e.g., Gumroad, AWS Marketplace)
- Direct sales to individuals and teams
- Immediate revenue potential
- Less visibility, smaller reach
- Full control over pricing and access

OPTION C: Hybrid (GitHub + Commercial)
- Open-source core on GitHub (builds community)
- Premium packs/features sold separately
- Enterprise consulting and custom roles
- Maximum reach + revenue potential

Question: Which strategy should we pursue and why?
"""
    
    tasks = [
        Task(
            description=f"As the Enterprise Risk Strategist, analyze the STRATEGIC RISKS and OPPORTUNITIES of each distribution option:\n\n{context}\n\nEvaluate market timing, competitive positioning, revenue potential, and sustainability. Which option maximizes long-term value while minimizing strategic risk?",
            expected_output="Strategic analysis with recommended option and rationale",
            agent=advisors[0],
        ),
        Task(
            description=f"As the Governance Analyst, evaluate the LEGAL and BUSINESS STRUCTURE implications:\n\n{context}\n\nConsider: How does Elastic License 2.0 interact with each option? What legal protections do we have? What business entity structure supports each model? What are the compliance obligations?",
            expected_output="Legal and governance framework analysis",
            agent=advisors[1],
        ),
        Task(
            description=f"As the Ethics Advisor, assess the ETHICAL DIMENSIONS:\n\n{context}\n\nConsider: What do we owe the community? Is it ethical to build in public then monetize? How do we balance 'giving back' with 'making a living'? What is the right thing to do for users, contributors, and ourselves?",
            expected_output="Ethical evaluation with principled recommendations",
            agent=advisors[2],
        ),
        Task(
            description=f"As the Data Storyteller, evaluate the MARKET POSITIONING and NARRATIVE for each option:\n\n{context}\n\nConsider: What story does each option tell? Which positioning is strongest? How do we message this to different audiences (developers, enterprises, investors)? What is the most compelling value proposition?",
            expected_output="Messaging strategy and positioning recommendations",
            agent=advisors[3],
        ),
    ]
    
    # Synthesis by Enterprise Risk Strategist
    synthesis = Task(
        description=f"SYNTHESIZE all evaluations into a final recommendation:\n\n{context}\n\nReview inputs from Risk Strategist, Governance Analyst, Ethics Advisor, and Data Storyteller.\n\nDeliver:\n1. FINAL RECOMMENDATION (Option A, B, or C)\n2. Top 3 reasons for the choice\n3. Implementation roadmap\n4. Success metrics\n5. Risks and mitigation\n\nBe decisive. We need to act.",
        expected_output="Final strategic recommendation with implementation plan",
        agent=advisors[0],
    )
    
    crew = Crew(agents=advisors, tasks=tasks + [synthesis], verbose=True)
    return crew.kickoff()


def main():
    print("=" * 70)
    print("DISTRIBUTION STRATEGY ADVISORY BOARD")
    print("=" * 70)
    print("\nEvaluating: GitHub vs Commercial Marketplace vs Hybrid")
    print("Using RoleForge's own agent roles as strategic advisors.\n")
    
    result = evaluate_distribution_strategy()
    
    # Save results
    output_path = Path("distribution_strategy_review.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# RoleForge Distribution Strategy Review\n\n")
        f.write("**Question:** Should we share on GitHub or sell on a commercial marketplace?\n\n")
        f.write(result)
    
    print(f"\n📄 Full report saved to: {output_path}")
    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)
    print(result)


if __name__ == "__main__":
    main()
