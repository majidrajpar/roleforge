# Changelog

All notable changes to RoleForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Pricing switched from one-time purchases to monthly subscriptions (cancel anytime)
- Professional Pack tier retired; lineup is now Individual → Domain Packs → Complete → Enterprise
- Governance domain expanded to 4 roles (Board Liaison, Governance Analyst, Ethics Advisor, Data Governance Specialist)
- Data Governance Specialist moved from Data Analysis to Governance
- BI Analyst belongs to Audit; Data Analysis now includes Statistical Reviewer
- Creative Writing Pack tightened to 4 roles (Narrative Architect, Character Developer, World Builder, Dialogue Specialist)

## [0.1.0] - 2026-06-25

### Added
- Initial release with 31 framework-agnostic agent roles across 7 domains
- Framework adapters for CrewAI, LangChain, and LangGraph
- RoleSelector with keyword-based and LLM-powered recommendation
- 9 pre-built LangGraph workflow templates
- JSON Schema + Pydantic validation for role definitions
- 43 unit tests covering models, loaders, registry, adapters, and graph templates
- Comprehensive documentation and usage examples

### Domains
- Audit (6 roles)
- Risk (5 roles)
- Governance (4 roles)
- Philosophy (4 roles)
- Creative Writing (4 roles)
- Book Writing (3 roles)
- Data Analysis (5 roles)

