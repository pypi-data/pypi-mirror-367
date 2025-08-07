# Package Preparation Prompt for AI Assistant

## Context Note
I have successfully renamed and published `pykit` as `pycaddy` on PyPI. Now I need help preparing another package called `quansys` for PyPI publication. This package likely still references the old `pykit` name and needs to be updated to use the published `pycaddy` package.

## Role & Instructions

**Role**: Python packaging expert and code refactoring specialist with expertise in PyPI publishing workflows.

**Goal**: Prepare the `quansys` package for PyPI publication by updating all references from `pykit` to `pycaddy` and ensuring proper project configuration.

## Phase 1: Initial Analysis & Renaming (REQUIRED FIRST)

### Actions:
1. **Repository Analysis**: Read through the entire codebase and identify ALL locations where `pykit` is referenced, including:
   - Import statements (`from pykit import ...`, `import pykit...`)
   - Dependencies in `pyproject.toml`, `requirements.txt`, or similar files
   - Documentation references in README files
   - Comments mentioning `pykit`
   - Any configuration files

2. **Systematic Replacement**: Replace ALL instances of `pykit` with `pycaddy`:
   - Update import statements: `from pykit.xxx` → `from pycaddy.xxx`
   - Update dependencies: `pykit` → `pycaddy` (since it's now on PyPI)
   - Update documentation references
   - Update comments and docstrings

3. **Project Configuration Update**: Update `pyproject.toml` to:
   - Set correct package name (`quansys`)
   - Replace any `pykit` dependencies with `pycaddy`
   - Ensure proper metadata (author, description, etc.)

4. **STOP HERE**: After completing the renaming, inform the user that Phase 1 is complete and wait for confirmation to proceed.

**User will then run:**
```bash
uv pip install -e .
ruff check .
```

**Only proceed to Phase 2 if user confirms ruff check passes.**

## Phase 2: PyPI Publishing Preparation (ONLY after user confirmation)

### Prerequisites Check:
- [ ] Phase 1 completed and ruff check passed
- [ ] User has confirmed to proceed

### Actions:
1. **Read Publishing Guide**: Carefully read the publishing guide that will be provided in the repository or by the user.

2. **PyPI Compliance Audit**:
   - [ ] Check `pyproject.toml` for proper PyPI metadata
   - [ ] Verify `LICENSE` file exists and is properly formatted
   - [ ] Check `README.md` for PyPI compatibility (installation instructions, usage examples)
   - [ ] Verify package structure and imports
   - [ ] Ensure Hatch build backend is configured:
     ```toml
     [build-system]
     requires = ["hatchling"]
     build-backend = "hatchling.build"
     ```

3. **Metadata Validation**:
   - Package name is unique and descriptive
   - Version follows semantic versioning (0.1.0 for first release)
   - Author information is complete
   - Dependencies are properly specified
   - Python version requirements are set
   - Proper classifiers for the package type

4. **Build System Check**:
   - Ensure modern Hatch backend is used (not setuptools)
   - License format uses simple string: `license = "MIT"` (not `{text = "MIT"}`)
   - No deprecated configuration patterns

5. **Final Recommendations**: Provide a summary of:
   - What was updated from `pykit` to `pycaddy`
   - Any issues found and fixed
   - Readiness status for PyPI publication
   - Next steps from the publishing guide

## Important Notes:
- **DO NOT** run `ruff check` or `pytest` - the user will handle code quality verification
- **DO NOT** execute any build or upload commands
- **STOP** after Phase 1 and wait for user confirmation before proceeding
- Focus on preparation and configuration, not code execution
- Be thorough in finding ALL `pykit` references - missing even one can cause import errors

## Package Information:
- **Current package name**: `quansys`
- **Old dependency**: `pykit` (needs replacement)
- **New dependency**: `pycaddy` (published on PyPI)
- **Target**: Prepare for PyPI publication

---

**Usage**: Copy this prompt and the publishing guide to your new repository, then ask the AI assistant to begin with Phase 1.