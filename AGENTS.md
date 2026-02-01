Agents / Contributor Guidance

All docs files are to be put into the `docs/` folder with the exception of `README.md` and `AGENTS.md`.

This repository uses the `crime` conda environment. Prefer `conda install` when adding packages; use `pip` only if a package is unavailable via conda.

Notebooks are considered unfinished until they are executed end-to-end with no errors. Commit notebooks with outputs cleared (see rules below) and push changes to the remote repository at logical file-level commits.

---

## Notebook Rules (for contributors and agents)

The following rules apply to creating, running, and committing Jupyter notebooks in this project. They ensure reproducibility, reviewability, and production-readiness.

1. **Purpose:** Notebooks must be reproducible analytical artifacts that can be executed end-to-end and used to generate report-quality outputs.

2. **Location:** Place all notebooks in the `notebooks/` directory. Exported visual assets and rendered reports must go to `reports/`.

3. **Environment:** Use the `crime` conda environment defined in `environment.yml`. Prefer `conda install` for packages; use `pip` only when `conda` fails. Record the environment name and key package versions in the notebook (see Reproducibility cell).

4. **Reproducibility Cell:** The first code cell must capture runtime metadata including Python version, conda env name, and versions of key libraries (pandas, numpy, scipy, matplotlib, seaborn, plotly). Example: print `sys.version` and a short `pip freeze` subset.

5. **Run Before Commit:** Every notebook must be executed start-to-finish locally (or in CI) with no errors before committing. If long-running steps exist, provide a fast/sampled dev path and clearly mark the long step.

6. **Outputs & Committed Files:** Commit notebooks with outputs cleared to avoid merge conflicts. Separately commit publication-ready exports (PNG/HTML/PDF) to `reports/` for review and reproducibility. Large binary artifacts should be reviewed and justified in PRs.

7. **Data Access:** Use project utilities (e.g., `analysis.utils.load_data`) and relative paths under `data/`. Document the data source, file path, and last update date in a metadata cell.

8. **Classification & Schemas:** Adhere to the project data schema and column naming conventions. Any schema changes must be documented and coordinated in PRs.

9. **Modularity:** Keep heavy data processing and reusable functions in `analysis/` modules. Notebooks should orchestrate processing, visualization, and interpretation, not contain large reusable code blocks.

10. **Style & Quality:** Follow PEP 8. Avoid `from module import *`. Use descriptive variable names and add short docstrings for custom helper functions. Keep notebook cells concise and focused.

11. **Notebook Structure:** Include, in order: title, short overview, table of contents, reproducibility cell, imports, data loading, data validation, transformation, analysis, visualizations (with saving), results/insights, and conclusion.

12. **Visualization Standards:** All plots must have clear titles, axis labels, legends, and consistent color palettes (use `analysis.config.COLORS` where available). Save figures at publication quality (300 DPI) to `reports/`.

13. **Data Quality & Validation:** Include checks for missingness, date ranges, coordinate validity, and other domain validations. Document filtering decisions and assumptions.

14. **Randomness & Seeds:** Set and document seeds for any stochastic processes to ensure reproducibility.

15. **Performance & Sampling:** For large datasets, provide a sampling/debug mode and document memory/CPU expectations. Flag long-running cells; provide progress indicators where helpful.

16. **CI & Headless Execution:** Notebooks should be runnable headless (e.g., `jupyter nbconvert --execute`) for CI. Add a small test-run mode that executes quickly with a sample of the data.

17. **Completion Checklist:** Each notebook must include (or reference) a completion checklist before merging: ran successfully, no errors, figures saved to `reports/`, reproducibility metadata present, outputs cleared, and PR summary written.

18. **Commit Messages & PRs:** Use descriptive commit messages and include an executive summary of the notebook findings in the PR description. Link to generated `reports/` assets in the PR.

19. **Ownership & Review:** Add an author/owner line in the notebook metadata. Major notebooks require at least one code review before merging.

20. **Privacy & Security:** Never include raw PII in committed notebooks or exported reports. Aggregate or anonymize sensitive information before saving or sharing.

21. **Documentation:** Update `docs/NOTEBOOK_COMPLETION_REPORT.md` and `docs/NOTEBOOK_QUICK_REFERENCE.md` with any notable deviations or new best practices introduced by the notebook.

These rules should be followed by all contributors and automated agents working on notebooks in this repository.
- All docs files are to be put into the docs/ folder with the exception o f the README.md and AGENTS.md file.
- All notebooks are not considered finsihed until they are ran and executed and all errors are cleared out and fixed. 
- this repo used conda environment crime
- default to conda install for packages, only use pip if conda install fails
- commit at the file level using standard commit messages and push all to remote repot at the end of each run. 