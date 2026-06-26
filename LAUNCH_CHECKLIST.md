# RoleForge Launch Checklist

## ✅ DONE

- [x] Git repo initialized with clean commit history
- [x] 31 roles validated across 7 domains
- [x] 43 tests passing
- [x] Free starter pack (3 roles) in `store/starter_pack/`
- [x] Paid product pages in `store/`
- [x] One-time pricing: $49 / $99 / $199 / $499
- [x] README, LICENSE, CONTRIBUTING, CHANGELOG ready
- [x] CI/CD workflow configured
- [x] Market research report generated

---

## 🔗 NEXT STEPS

### 1. Create GitHub Repository

```bash
# Go to https://github.com/new
# Name: roleforge
# Visibility: Public
# Description: 31 production-grade agent roles for CrewAI, LangChain, and LangGraph
```

Then run:

```bash
git remote add origin https://github.com/majidrajpar/roleforge.git
git branch -M main
git push -u origin main
```

### 2. Set Up Gumroad Store

1. Go to https://gumroad.com and create an account
2. Create products:
   - Domain Pack - $49
   - Professional Pack - $99
   - Complete Bundle - $199 (mark as "Best Value")
   - Enterprise License - $499
3. Upload the role files as ZIPs for each tier
4. Set "Can be updated" to YES (you'll add new roles over time)

### 3. Update Placeholder Links

Replace these in all files:

| File | Search | Replace With |
|---|---|---|
| README.md | `majidrajpar` | Your GitHub username |
| README.md | `majidrajpar@gmail.com` | Your real email |
| README.md | `majidrajpar.github.io/portfolio_my/roleforge/` | Your website |
| WEBSITE_DESCRIPTION.md | `majidrajpar` | Your GitHub username |
| WEBSITE_DESCRIPTION.md | `majidrajpar@gmail.com` | Your real email |
| WEBSITE_DESCRIPTION.md | `majidrajpar.github.io/portfolio_my/roleforge/` | Your website |
| COMMERCIAL_LICENSE.md | `majidrajpar@gmail.com` | Your real email |
| COMMERCIAL_LICENSE.md | `gumroad.com/your-store` | Your Gumroad store |
| store/**/*.md | `gumroad.com/your-store` | Your Gumroad store |
| store/**/*.md | `majidrajpar@gmail.com` | Your real email |

**Quick replace command:**

```bash
# Run from repo root
sed -i 's/majidrajpar/YOUR_ACTUAL_USERNAME/g' README.md WEBSITE_DESCRIPTION.md COMMERCIAL_LICENSE.md
sed -i 's/majidrajpar@gmail.com/YOUR_ACTUAL_EMAIL/g' README.md WEBSITE_DESCRIPTION.md COMMERCIAL_LICENSE.md store/**/*.md
sed -i 's/majidrajpar.github.io/portfolio_my/roleforge//YOUR_ACTUAL_WEBSITE/g' README.md WEBSITE_DESCRIPTION.md
sed -i 's|gumroad.com/your-store|gumroad.com/YOUR_ACTUAL_STORE|g' store/**/*.md COMMERCIAL_LICENSE.md
```

### 4. Launch Content

Post on:
- [ ] Hacker News (Show HN)
- [ ] Reddit r/LocalLLaMA, r/selfhosted
- [ ] LinkedIn with a demo video
- [ ] Twitter/X with a thread
- [ ] AI agent Discord servers

### 5. Track Metrics

Monitor:
- GitHub stars
- Gumroad sales
- Website visits (if you add analytics)
- Free tier downloads

---

## 📦 How to Package Role Bundles for Gumroad

Each paid tier needs a ZIP file with the role YAMLs + overlays:

```bash
# Example: Package Domain Pack (Audit)
cd store/domain_packs
mkdir audit_pack
cp ../../roles/audit/*.yaml audit_pack/
cp ../../overlays/crewai/*.yaml audit_pack/overlays/
cp ../../overlays/langgraph/*.yaml audit_pack/overlays/
zip -r audit_domain_pack.zip audit_pack/
```

Upload `audit_domain_pack.zip` to Gumroad as the Domain Pack product.

---

## 🎯 Launch Order

1. **Today:** Push to GitHub, replace placeholder links
2. **Day 1-3:** Set up Gumroad products
3. **Day 3-5:** Post on HN, Reddit, LinkedIn
4. **Week 1:** Monitor, iterate, respond to issues
5. **Week 2-4:** Build tiered store if Complete Bundle sells 50 units

---

## 🚀 Quick Commands

```bash
# Validate everything is ready
uv run python tools/validate_roles.py
uv run pytest tests/

# Commit link updates
git add -A
git commit -m "chore: replace placeholder links with real ones"
git push
```

**Good luck. Ship it.**
