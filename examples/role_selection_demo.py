"""
Demonstration of the Role Selector and LLM Role Recommender.
Shows how to point an LLM (or just a query) at the role library and get useful agent recommendations.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from role_selector import RoleSelector, LLMRoleRecommender
from crewai import LLM


# IMPORTANT: Set your API key via environment variable for LLM recommender
# export OLLAMA_API_KEY="your-api-key-here"
API_KEY = os.getenv("OLLAMA_API_KEY", "your-api-key-here")


def demo_basic_selector():
    """Demo 1: Basic keyword-based role selection."""
    print("=" * 60)
    print("DEMO 1: Basic Role Selection (Keyword Matching)")
    print("=" * 60)
    print()

    selector = RoleSelector()

    queries = [
        "I need to audit our cloud infrastructure for security risks",
        "Write a compelling story with deep characters",
        "Analyze our quarterly sales data and build a dashboard",
        "Evaluate whether our AI deployment is ethical",
        "Assess credit risk in our loan portfolio",
    ]

    for query in queries:
        print(f"Query: \"{query}\"")
        results = selector.recommend(query, top_k=3)
        print("Recommended roles:")
        for i, role in enumerate(results, 1):
            print(f"  {i}. {role['name']} ({role['category']}) - Score: {role['score']}")
            print(f"     Description: {role['description'][:80]}...")
        print()


def demo_team_composition():
    """Demo 2: Compose a multi-agent team for a complex task."""
    print("=" * 60)
    print("DEMO 2: Multi-Agent Team Composition")
    print("=" * 60)
    print()

    selector = RoleSelector()

    query = "We are writing a corporate governance policy for AI usage that needs to comply with GDPR and include ethical guidelines"

    print(f"Task: \"{query}\"")
    print("Recommended team (diverse categories):")
    print()

    team = selector.recommend_team(query, team_size=4)
    for i, member in enumerate(team, 1):
        print(f"  {i}. {member['name']} ({member['category']})")
        print(f"     Relevance Score: {member['score']}")
        print(f"     Expertise: {', '.join(member['expertise'][:3])}")
        print()


def demo_llm_recommender():
    """Demo 3: Use an LLM for semantic role recommendations."""
    print("=" * 60)
    print("DEMO 3: LLM-Based Role Recommender")
    print("=" * 60)
    print()

    api_key = API_KEY
    llm = LLM(
        model="kimi-k2.7-code:cloud",
        base_url="https://ollama.com/v1",
        api_key=api_key,
    )

    recommender = LLMRoleRecommender(llm=llm)

    query = "I need someone to evaluate the philosophical and ethical implications of deploying facial recognition technology in public spaces"

    print(f"Task: \"{query}\"")
    print()

    # LLM-powered recommendation
    print("LLM-Powered Recommendations:")
    results = recommender.recommend(query, top_k=3, use_llm=True)
    for i, role in enumerate(results, 1):
        print(f"  {i}. {role['name']} ({role['category']})")
        print(f"     Description: {role['description'][:100]}...")
        print()

    # Compare with keyword-only
    print("Keyword-Only Recommendations (for comparison):")
    keyword_results = recommender.recommend(query, top_k=3, use_llm=False)
    for i, role in enumerate(keyword_results, 1):
        print(f"  {i}. {role['name']} ({role['category']})")
        print(f"     Score: {role['score']}")
        print()


def demo_category_browsing():
    """Demo 4: Browse roles by category."""
    print("=" * 60)
    print("DEMO 4: Category Browsing")
    print("=" * 60)
    print()

    selector = RoleSelector()

    print("Available categories:")
    categories = selector.list_categories()
    for cat in categories:
        print(f"  - {cat}")
    print()

    # Show all philosophy roles
    print("Philosophy roles:")
    philosophy_roles = selector.list_roles_in_category("philosophy")
    for role in philosophy_roles:
        print(f"  - {role['name']}: {role['description']}")
    print()


def demo_role_details():
    """Demo 5: Get full details for a specific role."""
    print("=" * 60)
    print("DEMO 5: Role Details Lookup")
    print("=" * 60)
    print()

    selector = RoleSelector()

    role_id = "operational_risk_manager"
    role = selector.get_role_by_id(role_id)

    if role:
        print(f"Role: {role['name']}")
        print(f"ID: {role['id']}")
        print(f"Category: {role['category']}")
        print(f"\nDescription:\n{role['description']}")
        print(f"\nResponsibilities:")
        for resp in role['responsibilities']:
            print(f"  - {resp}")
        print(f"\nExpertise:")
        for exp in role['expertise']:
            print(f"  - {exp}")
        print(f"\nRecommended Tools: {role['recommended_tools']}")
    print()


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "AGENT ROLES LIBRARY" + " " * 25 + "║")
    print("║" + " " * 8 + "Role Selection & Recommendation Demo" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    demo_basic_selector()
    demo_team_composition()
    demo_category_browsing()
    demo_role_details()

    # LLM recommender requires API key - uncomment to run
    # demo_llm_recommender()

    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  1. Point any query at the RoleSelector to find matching agents")
    print("  2. Use recommend_team() for multi-agent composition")
    print("  3. LLMRoleRecommender adds semantic understanding on top of keywords")
    print("  4. Browse by category or look up specific role details")


if __name__ == "__main__":
    main()
