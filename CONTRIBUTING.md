# Contributing to RoleForge

Thank you for considering contributing to RoleForge! This document outlines the process and guidelines for contributing.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/majidrajpar/roleforge/issues)
- Include a clear description, steps to reproduce, and expected vs actual behavior
- Specify your Python version and framework versions (CrewAI, LangChain, LangGraph)

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`uv run pytest tests/`)
5. **Validate roles** (`uv run python tools/validate_roles.py`)
6. **Commit** (`git commit -m 'Add amazing feature'`)
7. **Push** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Adding a New Role

1. Create a YAML file in `roles/{category}/` following `schemas/role.schema.json`
2. Optionally create overlays in `overlays/crewai/` and/or `overlays/langgraph/`
3. Run `uv run python tools/validate_roles.py` to verify
4. Add tests in `tests/test_core.py` if the role introduces new patterns
5. Update `README.md` if the role count changes

### Code Style

- Follow PEP 8
- Use type hints where practical
- Keep functions focused and modular
- Document public APIs with docstrings

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Elastic License 2.0).

## Questions?

Open an issue or reach out via the contact link on the project website.
