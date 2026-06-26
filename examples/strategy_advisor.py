"""
RoleForge Strategy Advisor

Use RoleForge's own agent roles to get expert advice on business strategy,
commercialization, governance, and risk management.

This demonstrates the library's real-world utility by using its own roles
as a multi-disciplinary advisory board.
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
    
    # You can use environment variable or placeholder
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
    
    # Advisory board composition
    board_config = [
        ("enterprise_risk_strategist", "crewai"),  # Strategic planning
        ("governance_analyst", "crewai"),           # Business structure & compliance
        ("ethics_advisor", "crewai"),               # Ethical considerations
        ("data_storyteller", "crewai"),             # Messaging & positioning
        ("scenario_modeler", "crewai"),             # Future planning & stress testing
    ]
    
    advisors = []
    for role_id, framework in board_config:
        role, overlay = registry.get_role_with_overlay(role_id, framework)
        agent = adapter.adapt(role, overlay.data if overlay else None)
        advisors.append(agent)
    
    return advisors


def advise_on_commercialization():
    """Get the advisory board's opinion on commercialization strategy."""
    
    advisors = get_advisory_board()
    
    strategy = """
We are considering monetizing an open-source agent roles library (MIT license).
Current plan:
- Core library remains free and open-source
- Enterprise features: governance dashboard, custom roles, SLA support
- Revenue: subscriptions ($2K/month + $99/user) + custom development

Questions:
1. What are the top risks to this model?
2. How do we prevent competitors from simply copying our work?
3. What pricing strategy maximizes revenue without alienating the community?
4. Should we trademark the brand name?
"""
    
    tasks = [
        Task(
            description=f"As the Enterprise Risk Strategist, analyze the RISKS and VIABILITY of this commercialization strategy:\n\n{strategy}",
            expected_output="Risk assessment with mitigation strategies",
            agent=advisors[0],
        ),
        Task(
            description=f"As the Governance Analyst, evaluate the BUSINESS STRUCTURE and LEGAL IMPLICATIONS:\n\n{strategy}",
            expected_output="Governance framework recommendations",
            agent=advisors[1],
        ),
        Task(
            description=f"As the Ethics Advisor, assess the ETHICAL IMPLICATIONS of monetizing open-source work:\n\n{strategy}",
            expected_output="Ethical evaluation with recommendations",
            agent=advisors[2],
        ),
        Task(
            description=f"As the Data Storyteller, craft the MESSAGING and POSITIONING strategy:\n\n{strategy}",
            expected_output="Messaging strategy and positioning recommendations",
            agent=advisors[3],
        ),
        Task(
            description=f"As the Scenario Modeler, stress-test this strategy under adverse conditions:\n\n{strategy}\n\nWhat happens if:\n- A major competitor copies our code\n- The community forks and creates a free alternative\n- Enterprise customers demand lower prices\n- We need to pivot the business model?",
            expected_output="Scenario analysis with contingency plans",
            agent=advisors[4],
        ),
    ]
    
    crew = Crew(agents=advisors, tasks=tasks, verbose=True)
    result = crew.kickoff()
    
    return result


def advise_on_pricing(question: str = "How should we price our enterprise tier?"):
    """Get pricing strategy advice from the board."""
    
    advisors = get_advisory_board()
    
    task = Task(
        description=f"The board needs pricing advice:\n\n{question}\n\nContext: We have an open-source library (MIT) with enterprise features. Current pricing is $2K/month platform fee + $99/user/month.\n\nProvide recommendations from your expertise area.",
        expected_output="Pricing strategy recommendations",
        agent=advisors[0],  # Enterprise Risk Strategist
    )
    
    crew = Crew(agents=[advisors[0]], tasks=[task])
    return crew.kickoff()


def advise_on_competitive_defense(question: str = "How do we defend against competitors copying our open-source code?"):
    """Get competitive strategy advice."""
    
    advisors = get_advisory_board()
    
    task = Task(
        description=f"The board needs competitive strategy advice:\n\n{question}\n\nContext: Our core code is MIT licensed. Anyone can fork and compete. We need sustainable competitive advantage.",
        expected_output="Competitive defense strategy",
        agent=advisors[0],  # Enterprise Risk Strategist
    )
    
    crew = Crew(agents=[advisors[0]], tasks=[task])
    return crew.kickoff()


def main():
    print("=" * 70)
    print("ROLFORGE STRATEGY ADVISOR")
    print("=" * 70)
    print("\nUsing RoleForge's own agent roles as a multi-disciplinary advisory board")
    print("to solve business strategy challenges.\n")
    print("Available advisors:")
    print("  - Enterprise Risk Strategist (strategic planning)")
    print("  - Governance Analyst (business structure & compliance)")
    print("  - Ethics Advisor (ethical considerations)")
    print("  - Data Storyteller (messaging & positioning)")
    print("  - Scenario Modeler (future planning & stress testing)")
    print()
    
    # Example 1: Full commercialization review
    print("Example 1: Full Commercialization Strategy Review")
    print("-" * 50)
    result = advise_on_commercialization()
    print(result)
    
    # Save results
    with open("strategy_advice.md", "w", encoding="utf-8") as f:
        f.write("# RoleForge Strategy Advisory Board Report\n\n")
        f.write(result)
    
    print(f"\n📄 Results saved to: strategy_advice.md")


if __name__ == "__main__":
    main()
