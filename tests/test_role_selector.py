"""
Tests for the Role Selector and LLM Role Recommender.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Add project root
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import pytest

from role_selector import RoleSelector, LLMRoleRecommender


class TestRoleSelector:
    def test_init_and_index(self):
        selector = RoleSelector()
        roles = selector.registry.list_roles()
        assert len(roles) == 3  # Starter pack: 3 free roles

    def test_recommend_basic(self):
        selector = RoleSelector()
        results = selector.recommend("data analysis", top_k=3)
        assert len(results) > 0
        role_names = [r["name"] for r in results]
        assert any("Data" in name for name in role_names)

    def test_recommend_storytelling(self):
        selector = RoleSelector()
        results = selector.recommend("creative writing story", top_k=3)
        assert len(results) > 0
        assert results[0]["name"] == "Narrative Architect"
        assert results[0]["category"] == "creative_writing"

    def test_recommend_team_diversity(self):
        selector = RoleSelector()
        team = selector.recommend_team("write creative content with ethics", team_size=2)
        assert len(team) == 2
        categories = [m["category"] for m in team]
        assert len(set(categories)) >= 1

    def test_recommend_with_category_filter(self):
        selector = RoleSelector()
        results = selector.recommend(
            "data", top_k=3, category_filter="data_analysis"
        )
        assert len(results) > 0
        for r in results:
            assert r["category"] == "data_analysis"

    def test_list_categories(self):
        selector = RoleSelector()
        categories = selector.list_categories()
        assert "data_analysis" in categories
        assert "philosophy" in categories
        assert "creative_writing" in categories
        assert len(categories) == 3  # Starter pack categories

    def test_list_roles_in_category(self):
        selector = RoleSelector()
        roles = selector.list_roles_in_category("creative_writing")
        assert len(roles) == 1
        role_names = [r["name"] for r in roles]
        assert "Narrative Architect" in role_names

    def test_get_role_by_id(self):
        selector = RoleSelector()
        role = selector.get_role_by_id("data_scientist")
        assert role is not None
        assert role["name"] == "Data Scientist"

    def test_get_role_by_id_not_found(self):
        selector = RoleSelector()
        role = selector.get_role_by_id("nonexistent_role")
        assert role is None


class TestLLMRoleRecommender:
    def test_fallback_without_llm(self):
        recommender = LLMRoleRecommender(llm=None)
        results = recommender.recommend("data", top_k=3, use_llm=False)
        assert len(results) > 0

    def test_fallback_on_empty_llm(self):
        recommender = LLMRoleRecommender(llm=None)
        results = recommender.recommend("data", top_k=3, use_llm=True)
        assert len(results) > 0  # Should fallback to keyword matching


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
