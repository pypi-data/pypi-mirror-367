# PyPI Preparation Audit

**Date:** 2025-08-06  
**Maintainer:** uri.goldblatt@gmail.com  
**GitHub:** HutoriHunzu  
**License:** MIT  

## Package Name Research

### Original Name Issue
- **Current name:** `pykit` 
- **Issue:** Likely taken on PyPI (common generic name)
- **Search conducted:** Checked PyPI for alternatives

### Name Candidates Evaluated
Based on toolbox functionality (experiment tracking, automation, parameter sweeping):

| Name | Status | Notes |
|------|--------|-------|
| `runkit` | ❌ TAKEN | Active package for command-line utilities |
| `labkit` | ❌ TAKEN | Old package (2015) but still reserved |
| `expkit` | ✅ AVAILABLE | Best choice - relates to experiment tracking |
| `trackkit` | ✅ AVAILABLE | Good alternative |
| `autokit` | ✅ AVAILABLE | Broader automation focus |
| `studykit` | ✅ AVAILABLE | Academic research focus |

### **CHOSEN NAME: `pycaddy`** ✅
**Rationale:**
- Perfect metaphor: "caddy that holds your tools" - matches toolbox purpose
- Memorable and descriptive of functionality
- Available on PyPI (verified)
- Python-specific with "py" prefix
- Unique branding that differentiates from generic "kit" packages

---

# PyPI PREPARATION TODO LIST

## Phase 1: Package Naming & Structure
- [x] **1.0** VERIFIED `pycaddy` name availability ✅
  - [x] Confirmed: No `pycaddy` package exists on PyPI
  - [x] Verified: Available and unique name
- [ ] **1.1** Rename package from `pykit` to `pycaddy`
  - [ ] Update `pyproject.toml` name field
  - [ ] Rename `src/pykit/` directory to `src/pycaddy/`
  - [ ] Update all import statements in code
  - [ ] Update `CLAUDE.md` references
  - [ ] Update README.md references

## Phase 2: PyPI Compliance Setup
- [ ] **2.1** Create/Update `pyproject.toml` for PyPI
  - [ ] Set name = "pycaddy"
  - [ ] Add proper version (suggest 0.1.0 for initial release)
  - [ ] Add description field
  - [ ] Add author email: uri.goldblatt@gmail.com
  - [ ] Add license = "MIT"
  - [ ] Add homepage/repository URLs
  - [ ] Add classifiers for Python versions, development status
  - [ ] Review and clean dependencies list

- [ ] **2.2** Create `LICENSE` file
  - [ ] Add MIT License text
  - [ ] Include copyright with your name and year

- [ ] **2.3** Update/Create `README.md` for PyPI
  - [ ] Add installation instructions: `pip install expkit`
  - [ ] Add basic usage examples
  - [ ] Add minimal documentation links
  - [ ] Keep it concise (minimal effort approach)

## Phase 3: Code Quality & Distribution
- [ ] **3.1** Clean up codebase for distribution
  - [ ] Remove any `.idea/` or other IDE files from git
  - [ ] Update `.gitignore` if needed
  - [ ] Remove development files not needed for distribution
  - [ ] Ensure `__init__.py` files have proper imports

- [ ] **3.2** Version and build setup
  - [ ] Ensure `setup.py` not needed (using modern pyproject.toml)
  - [ ] Test local build: `python -m build`
  - [ ] Test local installation: `pip install -e .`

## Phase 4: Testing & Final Checks
- [ ] **4.1** Run existing tests
  - [ ] Execute: `python -m pytest tests/`
  - [ ] Fix any import issues from renaming
  - [ ] Ensure all tests pass

- [ ] **4.2** PyPI upload preparation
  - [ ] Install twine: `pip install twine`
  - [ ] Create PyPI account if needed
  - [ ] Test upload to TestPyPI first: `twine upload --repository testpypi dist/*`
  - [ ] Verify TestPyPI installation works

## Phase 5: Official PyPI Release
- [ ] **5.1** Final release
  - [ ] Build final distribution: `python -m build`
  - [ ] Upload to PyPI: `twine upload dist/*`
  - [ ] Verify installation: `pip install expkit`
  - [ ] Test in clean environment

---

## Minimal Effort Approach Notes

Since this is a dependency toolbox with minimal documentation needs:

1. **README**: Keep basic - `pip install pycaddy`, one example, link to existing docs
2. **Documentation**: Reference existing detailed documentation in other repos
3. **Testing**: Use existing test suite, no need for extensive CI/CD initially
4. **Versioning**: Start simple with 0.1.0, use semantic versioning
5. **Dependencies**: Keep current minimal dependency list

## Key Files to Create/Modify

1. `pyproject.toml` - Update name, metadata, licensing
2. `LICENSE` - MIT license file  
3. `README.md` - Minimal PyPI-friendly version
4. All Python files - Update imports from `pykit` to `pycaddy`
5. `CLAUDE.md` - Update package name references

## Risk Assessment

**LOW RISK:** Straightforward renaming and metadata updates  
**MEDIUM RISK:** Import statement updates across codebase  
**MITIGATION:** Test thoroughly after renaming, run full test suite

---

**Estimated Effort:** 2-3 hours for complete PyPI preparation  
**Priority Tasks:** Naming, pyproject.toml, LICENSE, imports update