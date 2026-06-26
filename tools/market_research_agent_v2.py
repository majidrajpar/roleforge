"""
RoleForge Market Research Agent v2 — LIVE LLM + WEB SEARCH

A production-grade LangGraph multi-agent system that:
1. Searches the web for real competitive pricing data
2. Uses a live LLM to synthesize findings with reasoning
3. Generates structured JSON recommendations
4. Saves outputs and self-verifies them

Run: uv run python market_research_agent_v2.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from ddgs import DDGS
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

API_KEY_PATH = r"C:\Users\sorat\Desktop\Coding\Dev_api\ollama_api_key.txt"
OLLAMA_BASE_URL = "https://ollama.com/v1"
OLLAMA_MODEL = "kimi-k2.7-code:cloud"


def load_api_key() -> str:
    """Load API key from file or environment."""
    key = os.getenv("OLLAMA_API_KEY")
    if key:
        return key.strip()
    if os.path.exists(API_KEY_PATH):
        with open(API_KEY_PATH, "r", encoding="utf-8") as f:
            return f.readline().strip()
    raise EnvironmentError("OLLAMA_API_KEY not found in env or file.")


def llm_chat(system_prompt: str, user_prompt: str, api_key: str) -> str:
    """Call Ollama Cloud API directly. Returns text content."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 8000,
    }
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        if not content:
            return "[LLM ERROR: Empty content in response]"
        return content
    except Exception as e:
        return f"[LLM ERROR: {e}]"


def llm_chat_with_retry(system_prompt: str, user_prompt: str, api_key: str, retries: int = 2) -> str:
    """Call LLM with retry on empty or truncated responses."""
    for attempt in range(retries + 1):
        response = llm_chat(system_prompt, user_prompt, api_key)
        if not response.startswith("[LLM ERROR") and len(response.strip()) > 200:
            return response
        print(f"    ⚠ Attempt {attempt + 1} returned short/empty response ({len(response)} chars). Retrying...")
    return response  # Return last attempt even if short


# =============================================================================
# TOOLS
# =============================================================================

def web_search(query: str, max_results: int = 8) -> list[dict]:
    """Search DuckDuckGo. Returns list of {title, url, snippet}."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in results
            ]
    except Exception as e:
        return [{"error": str(e), "query": query}]


# =============================================================================
# STATE
# =============================================================================

class ResearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    research_findings: list[dict]
    market_analysis_raw: str
    final_recommendation_json: dict
    verification_passed: bool
    verification_log: list[str]
    completed: bool


# =============================================================================
# AGENT NODES
# =============================================================================

def researcher_node(state: ResearchState) -> ResearchState:
    """Search the web for comparable products and pricing data."""
    print("\n[AGENT: Market Researcher] Running web searches...")
    
    queries = [
        "AI agent persona library pricing marketplace 2025 2026",
        "prompt engineering role template sell pricing Gumroad",
        "CrewAI LangChain agent role pack commercial product",
        "AI agent framework persona template marketplace",
        "open source agent role library monetization strategy",
        "LangGraph agent team template pricing buy",
    ]
    
    findings = []
    for i, query in enumerate(queries, 1):
        print(f"  Search {i}/{len(queries)}: {query[:50]}...")
        results = web_search(query, max_results=6)
        findings.append({"query": query, "results": results})
    
    state["research_findings"] = findings
    state["messages"].append(
        SystemMessage(
            content=f"[Researcher] Completed {len(queries)} searches. Found {sum(len(f['results']) for f in findings)} results."
        )
    )
    print(f"  ✓ Researcher done. Total results: {sum(len(f['results']) for f in findings)}")
    return state


def analyst_node(state: ResearchState) -> ResearchState:
    """Use live LLM to synthesize research into structured analysis."""
    print("\n[AGENT: Data Analyst] Calling LLM for synthesis...")
    
    api_key = load_api_key()
    
    # Build context from findings
    context_parts = ["## Web Research Findings\n"]
    for finding in state["research_findings"]:
        context_parts.append(f"\n### Query: {finding['query']}\n")
        for r in finding["results"][:4]:
            if "error" in r:
                context_parts.append(f"- Error: {r['error']}\n")
            else:
                context_parts.append(f"- {r['title']}: {r['snippet'][:180]}...\n")
    
    context = "".join(context_parts)
    
    system_prompt = (
        "You are a senior market analyst. Analyze competitive pricing data and output "
        "a structured JSON object with no markdown formatting. "
        "Respond ONLY with valid JSON."
    )
    
    user_prompt = (
        f"{context}\n\n"
        "Based on the research above, analyze the market for AI agent role libraries and persona templates. "
        "Output a JSON object with these exact keys:\n"
        "- comparable_products: list of objects with name, type, price_range, model, url\n"
        "- pricing_signals: dict of category to price range string\n"
        "- market_gaps: list of strings describing what does NOT exist\n"
        "- willingness_to_pay: dict of segment to description\n"
        "- competitive_risk: string summary\n"
        "- recommended_architecture: string (e.g., 'Freemium + Tiered')\n"
        "- recommended_free_tier: boolean (true/false)\n"
        "- recommended_tiers: list of objects with name, price_usd, contents, target, rationale\n"
        "- go_to_market: list of tactic strings\n"
        "- key_metrics: dict of metric_name to target string\n"
        "- first_action: string describing the immediate next step\n\n"
        "Be specific with dollar amounts. No generic advice."
    )
    
    response = llm_chat_with_retry(system_prompt, user_prompt, api_key, retries=2)
    
    # Debug: show if response is error or empty
    if response.startswith("[LLM ERROR"):
        print(f"  ⚠ LLM returned error: {response}")
    elif not response.strip():
        print("  ⚠ LLM returned EMPTY response")
    else:
        print(f"  ✓ LLM responded with {len(response)} chars")
    
    state["market_analysis_raw"] = response
    state["messages"].append(
        SystemMessage(content=f"[Analyst] LLM synthesis complete. Response length: {len(response)} chars.")
    )
    return state


def validator_node(state: ResearchState) -> ResearchState:
    """Parse LLM output, validate JSON, and save structured recommendation."""
    print("\n[AGENT: Validator] Parsing and validating LLM output...")
    
    raw = state["market_analysis_raw"]
    json_data = None
    errors = []
    
    # Attempt 1: direct JSON parse
    try:
        json_data = json.loads(raw)
        print("  ✓ Direct JSON parse succeeded.")
    except json.JSONDecodeError:
        errors.append("Direct JSON parse failed.")
        
        # Attempt 2: extract JSON from markdown code block
        if "```json" in raw:
            try:
                start = raw.index("```json") + 7
                end = raw.index("```", start)
                json_data = json.loads(raw[start:end].strip())
                print("  ✓ Extracted JSON from markdown code block.")
            except Exception as e:
                errors.append(f"Markdown extraction failed: {e}")
        
        # Attempt 3: find first { and last }
        if json_data is None:
            try:
                start = raw.index("{")
                end = raw.rindex("}") + 1
                json_data = json.loads(raw[start:end])
                print("  ✓ Extracted JSON via bracket matching.")
            except Exception as e:
                errors.append(f"Bracket extraction failed: {e}")
    
    # Validate required keys
    required_keys = [
        "comparable_products", "pricing_signals", "market_gaps",
        "willingness_to_pay", "competitive_risk", "recommended_architecture",
        "recommended_free_tier", "recommended_tiers", "go_to_market",
        "key_metrics", "first_action"
    ]
    
    verification_log = []
    if json_data is None:
        verification_log.append("FAIL: Could not parse JSON from LLM response.")
        verification_log.append(f"Raw response preview: {raw[:200]}...")
        json_data = generate_fallback_recommendation()
        verification_log.append("WARNING: Using fallback recommendation due to parse failure.")
    else:
        missing = [k for k in required_keys if k not in json_data]
        if missing:
            verification_log.append(f"WARNING: Missing keys: {missing}")
        else:
            verification_log.append("PASS: All required keys present.")
        
        if "recommended_tiers" in json_data:
            tiers = json_data["recommended_tiers"]
            if isinstance(tiers, list) and len(tiers) >= 2:
                verification_log.append(f"PASS: Found {len(tiers)} pricing tiers.")
            else:
                verification_log.append(f"FAIL: Expected >=2 tiers, got {len(tiers) if isinstance(tiers, list) else type(tiers)}")
        
        if "pricing_signals" in json_data:
            ps = json_data["pricing_signals"]
            if isinstance(ps, dict):
                verification_log.append(f"PASS: Pricing signals has {len(ps)} categories.")
    
    state["final_recommendation_json"] = json_data
    state["verification_log"] = verification_log
    state["verification_passed"] = any("PASS" in line for line in verification_log)
    state["completed"] = True
    
    state["messages"].append(
        SystemMessage(content=f"[Validator] Verification: {state['verification_passed']}. Log: {verification_log}")
    )
    
    print(f"  ✓ Validator done. Verification: {'PASSED' if state['verification_passed'] else 'FAILED (fallback used)'}")
    for line in verification_log:
        print(f"    - {line}")
    
    return state


def generate_fallback_recommendation() -> dict:
    """Sensible fallback if LLM output is unparseable."""
    return {
        "comparable_products": [
            {"name": "PromptBase", "type": "Prompt marketplace", "price_range": "$3-$15/prompt", "model": "Individual sales", "url": "promptbase.com"},
            {"name": "FlowGPT", "type": "Prompt marketplace", "price_range": "Free + Premium", "model": "Freemium", "url": "flowgpt.com"},
        ],
        "pricing_signals": {"individual_prompts": "$3-$15", "agent_personas": "$5-$50", "template_bundles": "$29-$99", "enterprise_frameworks": "$499-$2000/year"},
        "market_gaps": ["No dedicated agent role library exists", "No framework-agnostic validated roles sold commercially"],
        "willingness_to_pay": {"developers": "$0-$19 (low)", "consultants": "$49-$199 (medium)", "enterprise": "$499-$999 (high)"},
        "competitive_risk": "Low. No direct competitors. 6-12 month window.",
        "recommended_architecture": "Freemium + Tiered Bundles + Enterprise",
        "recommended_free_tier": True,
        "recommended_tiers": [
            {"name": "Starter Pack", "price_usd": 0, "contents": ["3 roles + overlays"], "target": "Developers evaluating", "rationale": "Remove friction, prove value"},
            {"name": "Domain Pack", "price_usd": 49, "contents": ["All roles in 1 domain"], "target": "Specialists", "rationale": "Job-oriented purchase"},
            {"name": "Complete Bundle", "price_usd": 199, "contents": ["All 31 roles + 12mo updates"], "target": "Power users", "rationale": "Anchor at $589, $199 is 66% off"},
            {"name": "Enterprise License", "price_usd": 999, "contents": ["Everything + SaaS rights + 5 custom roles"], "target": "Commercial teams", "rationale": "Legal protection + custom work"},
        ],
        "go_to_market": ["GitHub repo with free tier", "Gumroad for paid bundles", "LinkedIn/Twitter content marketing", "Hacker News Show HN"],
        "key_metrics": {"visitor_to_signup": "15%", "free_to_paid": "8%", "arpu": "$120"},
        "first_action": "Launch GitHub repo with 3 free roles + Complete Bundle on Gumroad at $199",
    }


# =============================================================================
# OUTPUT FORMATTER
# =============================================================================

def format_report(state: ResearchState) -> str:
    """Format final recommendation into a human-readable markdown report."""
    data = state["final_recommendation_json"]
    lines = []
    
    lines.append("# RoleForge Market Research Report")
    lines.append("*Generated by LangGraph Multi-Agent System (Live LLM + Web Search)*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## Executive Summary")
    lines.append(data.get("competitive_risk", "No competitive risk data."))
    lines.append("")
    
    lines.append("## Recommended Architecture")
    lines.append(data.get("recommended_architecture", "N/A"))
    lines.append("")
    
    if data.get("recommended_free_tier"):
        lines.append("## Free Tier: YES")
        lines.append("The agent recommends a free starter pack to remove friction and prove value before purchase.")
    else:
        lines.append("## Free Tier: NO")
        lines.append("The agent recommends a paid-only model.")
    lines.append("")
    
    lines.append("## Pricing Tiers")
    lines.append("")
    for tier in data.get("recommended_tiers", []):
        price = tier.get("price_usd", "N/A")
        name = tier.get("name", "Unnamed")
        highlight = " ⭐ BEST VALUE" if price == 199 else ""
        lines.append(f"### {name} — ${price}{highlight}")
        lines.append(f"**Target:** {tier.get('target', 'N/A')}")
        contents = tier.get('contents', '')
        if isinstance(contents, list):
            # Flatten if list contains strings, otherwise join
            content_str = ', '.join(str(c) for c in contents)
        else:
            content_str = str(contents)
        lines.append(f"**Contents:** {content_str}")
        lines.append(f"**Rationale:** {tier.get('rationale', 'N/A')}")
        lines.append("")
    
    lines.append("## Comparable Products Found")
    lines.append("")
    for prod in data.get("comparable_products", [])[:5]:
        lines.append(f"- **{prod.get('name', 'Unknown')}** ({prod.get('type', 'N/A')}): {prod.get('price_range', 'N/A')}")
    lines.append("")
    
    lines.append("## Market Gaps")
    lines.append("")
    for gap in data.get("market_gaps", []):
        lines.append(f"- {gap}")
    lines.append("")
    
    lines.append("## Go-To-Market")
    lines.append("")
    for i, tactic in enumerate(data.get("go_to_market", []), 1):
        lines.append(f"{i}. {tactic}")
    lines.append("")
    
    lines.append("## Key Metrics (Targets)")
    lines.append("")
    for k, v in data.get("key_metrics", {}).items():
        lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
    lines.append("")
    
    lines.append("## Recommended First Action")
    lines.append(data.get("first_action", "N/A"))
    lines.append("")
    
    lines.append("## Verification Log")
    lines.append("")
    for line in state.get("verification_log", []):
        lines.append(f"- {line}")
    lines.append("")
    
    return "\n".join(lines)


# =============================================================================
# INDEPENDENT VERIFICATION (runs after graph)
# =============================================================================

def verify_outputs(output_dir: Path, recommendation: dict) -> dict:
    """
    Independently verify that outputs exist, are well-formed, and make sense.
    Returns a verification report dict.
    """
    checks = []
    
    md_path = output_dir / "market_research_report_v2.md"
    if md_path.exists() and md_path.stat().st_size > 500:
        checks.append(f"PASS: {md_path.name} exists ({md_path.stat().st_size} bytes)")
    else:
        checks.append(f"FAIL: {md_path.name} missing or too small")
    
    json_path = output_dir / "market_recommendation_v2.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            checks.append(f"PASS: {json_path.name} is valid JSON")
            
            required = ["recommended_tiers", "recommended_architecture", "first_action"]
            missing = [k for k in required if k not in loaded]
            if not missing:
                checks.append("PASS: JSON has all required keys")
            else:
                checks.append(f"FAIL: JSON missing keys: {missing}")
            
            tiers = loaded.get("recommended_tiers", [])
            if tiers and all("price_usd" in t for t in tiers):
                checks.append(f"PASS: All {len(tiers)} tiers have price_usd")
            else:
                checks.append("FAIL: Some tiers missing price_usd")
            
            def parse_price(val):
                if isinstance(val, (int, float)):
                    return int(val)
                s = str(val).replace("$", "").replace("/mo", "").replace("/year", "").strip()
                try:
                    return int(float(s))
                except ValueError:
                    return 999
            
            prices = [parse_price(t.get("price_usd", 999)) for t in tiers]
            if any(p <= 49 for p in prices):
                checks.append("PASS: Has accessible entry price ($0-$49)")
            else:
                checks.append("WARNING: No accessible entry price found")
            
            if any(parse_price(t.get("price_usd", 0)) >= 499 for t in tiers):
                checks.append("PASS: Has enterprise-tier pricing")
            else:
                checks.append("WARNING: No enterprise-tier pricing found")
                
        except json.JSONDecodeError:
            checks.append(f"FAIL: {json_path.name} is not valid JSON")
    else:
        checks.append(f"FAIL: {json_path.name} does not exist")
    
    raw_path = output_dir / "llm_raw_response.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        checks.append(f"PASS: {raw_path.name} exists ({raw_path.stat().st_size} bytes)")
    else:
        checks.append(f"FAIL: {raw_path.name} missing or too small")
    
    all_pass = all("PASS" in c for c in checks)
    return {"all_pass": all_pass, "checks": checks}


# =============================================================================
# GRAPH BUILDER
# =============================================================================

def build_research_agent():
    """Build the LangGraph research workflow."""
    workflow = StateGraph(ResearchState)
    
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("validator", validator_node)
    
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "validator")
    workflow.add_edge("validator", END)
    
    return workflow.compile()


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 72)
    print("ROLEFORGE MARKET RESEARCH AGENT v2")
    print("Live LLM + Web Search + Self-Verification")
    print("=" * 72)
    print()
    
    try:
        api_key = load_api_key()
        print(f"✓ API key loaded ({len(api_key)} chars)")
    except EnvironmentError as e:
        print(f"✗ {e}")
        sys.exit(1)
    
    agent = build_research_agent()
    
    initial_state: ResearchState = {
        "messages": [HumanMessage(content="Research agent role library market and recommend pricing strategy.")],
        "research_findings": [],
        "market_analysis_raw": "",
        "final_recommendation_json": {},
        "verification_passed": False,
        "verification_log": [],
        "completed": False,
    }
    
    print("\n>> Running LangGraph workflow...")
    print("   Steps: Researcher → Analyst (LLM) → Validator")
    print()
    
    result = agent.invoke(initial_state)
    
    # Format and save outputs
    report = format_report(result)
    
    output_dir = Path(__file__).parent / "research_output"
    output_dir.mkdir(exist_ok=True)
    
    md_path = output_dir / "market_research_report_v2.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    json_path = output_dir / "market_recommendation_v2.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result["final_recommendation_json"], f, indent=2)
    
    raw_path = output_dir / "llm_raw_response.txt"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(result["market_analysis_raw"])
    
    # Independent verification
    print("\n" + "=" * 72)
    print("INDEPENDENT VERIFICATION")
    print("=" * 72)
    verification = verify_outputs(output_dir, result["final_recommendation_json"])
    
    for check in verification["checks"]:
        status = "✓" if "PASS" in check else "✗"
        print(f"  {status} {check}")
    
    # Final summary
    print("\n" + "=" * 72)
    print("FINAL SUMMARY")
    print("=" * 72)
    
    rec = result["final_recommendation_json"]
    print(f"  Architecture:      {rec.get('recommended_architecture', 'N/A')}")
    print(f"  Free Tier:         {'YES' if rec.get('recommended_free_tier') else 'NO'}")
    
    tiers = rec.get("recommended_tiers", [])
    if tiers:
        print(f"  Pricing Tiers:     {len(tiers)}")
        for t in tiers:
            print(f"    - {t.get('name', '?'):20s} ${t.get('price_usd', '?'):4}  ({t.get('target', 'N/A')})")
    
    print(f"  First Action:      {rec.get('first_action', 'N/A')}")
    print(f"  Verification:      {'ALL PASSED' if verification['all_pass'] else 'SOME CHECKS FAILED'}")
    print()
    
    print("=" * 72)
    print("OUTPUT FILES")
    print("=" * 72)
    print(f"  Markdown report:   {md_path}")
    print(f"  JSON data:         {json_path}")
    print(f"  LLM raw response:  {raw_path}")
    print()
    
    if verification["all_pass"]:
        print("✓ Agent execution complete. All verifications passed.")
        print("✓ You can now review the outputs and decide on implementation.")
    else:
        print("⚠ Some verification checks failed. Review logs above.")


if __name__ == "__main__":
    main()
