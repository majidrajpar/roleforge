"""
Role Recommender for the Agent Roles Library.
Analyzes user queries and suggests the most relevant agent roles.
"""
from __future__ import annotations

from typing import Any
from collections import Counter

from models import RoleDefinition, RuntimeContext
from loader import RoleRegistry


class RoleSelector:
    """
    Recommends agent roles based on user queries.
    Supports keyword matching, semantic analysis, and team composition.
    """

    def __init__(self, registry: RoleRegistry | None = None):
        self.registry = registry or RoleRegistry()
        self.registry.index()

    def recommend(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0,
        category_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Recommend roles based on keyword and semantic matching.
        Returns ranked list of roles with relevance scores.
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        candidates = self.registry.list_roles()

        # Optional category filter
        if category_filter:
            candidates = [r for r in candidates if r.category == category_filter]

        scored_roles = []
        for role in candidates:
            score = self._calculate_relevance(role, query_terms, query_lower)
            if score >= min_score:
                scored_roles.append((role, score))

        # Sort by score descending
        scored_roles.sort(key=lambda x: x[1], reverse=True)

        results = []
        for role, score in scored_roles[:top_k]:
            results.append({
                "id": role.id,
                "name": role.name,
                "category": role.category,
                "description": role.description,
                "score": round(score, 3),
                "expertise": role.expertise,
                "responsibilities": role.responsibilities,
            })

        return results

    def recommend_team(
        self,
        query: str,
        team_size: int = 3,
        category_diversity: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Recommend a diverse team of roles that complement each other.
        Ensures coverage across different expertise areas.
        """
        all_results = self.recommend(query, top_k=20, min_score=0.1)

        if not all_results:
            return []

        team = []
        used_categories = set()

        for candidate in all_results:
            if len(team) >= team_size:
                break

            # If diversity requested, prefer new categories
            if category_diversity and candidate["category"] in used_categories:
                continue

            team.append(candidate)
            used_categories.add(candidate["category"])

        # Fill remaining slots with best candidates regardless of category
        if len(team) < team_size:
            for candidate in all_results:
                if len(team) >= team_size:
                    break
                if candidate["id"] not in [m["id"] for m in team]:
                    team.append(candidate)

        return team

    def _calculate_relevance(
        self,
        role: RoleDefinition,
        query_terms: set[str],
        query_lower: str,
    ) -> float:
        """
        Calculate relevance score between role and query.
        Combines multiple signals: keyword overlap, category match,
        tag match, and description similarity.
        """
        score = 0.0

        # 1. Name match (high weight)
        name_words = set(role.name.lower().split())
        name_overlap = len(query_terms & name_words)
        score += name_overlap * 3.0

        # 2. Category match (high weight)
        if role.category.lower() in query_lower:
            score += 2.0

        # 3. Domain tags match (medium weight)
        tag_matches = sum(1 for tag in role.domain_tags if tag.lower() in query_lower)
        score += tag_matches * 1.5

        # 4. Description keyword overlap (medium weight)
        desc_words = set(role.description.lower().split())
        desc_overlap = len(query_terms & desc_words)
        score += desc_overlap * 0.5

        # 5. Responsibility overlap (medium weight)
        resp_matches = 0
        for resp in role.responsibilities:
            resp_lower = resp.lower()
            if any(term in resp_lower for term in query_terms):
                resp_matches += 1
        score += resp_matches * 1.0

        # 6. Expertise overlap (medium weight)
        exp_matches = 0
        for exp in role.expertise:
            if any(term in exp.lower() for term in query_terms):
                exp_matches += 1
        score += exp_matches * 1.0

        return score

    def get_role_by_id(self, role_id: str) -> dict[str, Any] | None:
        """Get full role details by ID."""
        role = self.registry.get(role_id)
        if not role:
            return None

        return {
            "id": role.id,
            "name": role.name,
            "category": role.category,
            "description": role.description,
            "responsibilities": role.responsibilities,
            "expertise": role.expertise,
            "recommended_tools": role.recommended_tools,
            "domain_tags": role.domain_tags,
        }

    def list_categories(self) -> list[str]:
        """Return all available role categories."""
        roles = self.registry.list_roles()
        return sorted(set(r.category for r in roles))

    def list_roles_in_category(self, category: str) -> list[dict[str, Any]]:
        """List all roles in a specific category."""
        roles = self.registry.list_roles()
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description[:100] + "...",
            }
            for r in roles
            if r.category == category
        ]


class LLMRoleRecommender:
    """
    Advanced role recommender that uses an LLM for semantic matching.
    Falls back to keyword matching if no LLM is provided.
    """

    def __init__(self, llm: Any | None = None, registry: RoleRegistry | None = None):
        self.llm = llm
        self.selector = RoleSelector(registry)

    def recommend(
        self,
        query: str,
        top_k: int = 3,
        use_llm: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Recommend roles using LLM-based semantic analysis.
        """
        if not use_llm or self.llm is None:
            # Fall back to keyword matching
            return self.selector.recommend(query, top_k=top_k)

        # Use LLM for semantic analysis
        roles = self.selector.registry.list_roles()
        role_summaries = []
        for role in roles:
            summary = f"ID: {role.id} | Name: {role.name} | Category: {role.category} | Description: {role.description[:150]}..."
            role_summaries.append(summary)

        # Build prompt for LLM
        prompt = self._build_recommendation_prompt(query, role_summaries)

        # Call LLM
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return self._parse_llm_response(content, roles, top_k)
        except Exception:
            # Fall back to keyword matching on error
            return self.selector.recommend(query, top_k=top_k)

    def _build_recommendation_prompt(
        self,
        query: str,
        role_summaries: list[str],
    ) -> str:
        """Build a prompt for the LLM to recommend roles."""
        prompt = (
            "You are an expert system that matches user tasks with the most suitable agent roles.\n\n"
            f"User Task: {query}\n\n"
            "Available Roles:\n"
        )
        for summary in role_summaries:
            prompt += f"- {summary}\n"
        prompt += (
            "\nBased on the user's task, recommend the TOP 3 most relevant roles.\n"
            "Respond ONLY with the role IDs in order of relevance, one per line.\n"
            "Format:\n"
            "1. [role_id]\n"
            "2. [role_id]\n"
            "3. [role_id]\n"
        )
        return prompt

    def _parse_llm_response(
        self,
        content: str,
        roles: list[RoleDefinition],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Parse LLM response to extract recommended role IDs."""
        lines = content.strip().split("\n")
        recommended_ids = []

        for line in lines:
            line = line.strip()
            # Remove numbering like "1. " or "- "
            if line and (line[0].isdigit() or line.startswith("-")):
                parts = line.split()
                if len(parts) > 1:
                    role_id = parts[-1].strip("[]")  # Handle [role_id] format
                    recommended_ids.append(role_id)

        results = []
        role_map = {r.id: r for r in roles}

        for idx, role_id in enumerate(recommended_ids[:top_k]):
            if role_id in role_map:
                role = role_map[role_id]
                results.append({
                    "id": role.id,
                    "name": role.name,
                    "category": role.category,
                    "description": role.description,
                    "score": round(1.0 - (idx * 0.1), 2),  # Descending score
                    "expertise": role.expertise,
                    "responsibilities": role.responsibilities,
                })

        return results
