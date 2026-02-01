---
description: Instructions for processing and generating Jupyter notebooks in the Crime Incidents Philadelphia project
applyTo: '*.ipynb'
---

# Jupyter Notebook Processing Instructions

These instructions guide AI assistants when working with Jupyter notebooks in the Crime Incidents Philadelphia data analysis project. Follow these best practices to ensure high-quality, reproducible, and maintainable notebook code.

## General Best Practices

1. **Structure and Organization**
   - Start notebooks with a clear title and overview in the first markdown cell
   - Include a table of contents at the beginning of the notebook for easy navigation
   - Use markdown cells to separate logical sections with descriptive headings
   - Group related code cells together and add explanatory markdown between sections
   - End with a summary or conclusions section

2. **Code Quality**
   - Follow PEP 8 style guidelines for Python code
   - Use descriptive variable and function names
   - Add comments for complex logic or non-obvious code
   - Keep functions and classes in separate .py files when they become substantial
   - Use type hints where appropriate

3. **Imports and Dependencies**
   - Import all required libraries at the top of the notebook
   - Group imports logically (standard library, third-party, local)
   - Avoid wildcard imports (from module import *)
   - Check for unused imports and remove them

4. **Data Handling**
   - Use relative paths for data files within the project structure
   - Load data efficiently, considering memory constraints
   - Validate data integrity after loading
   - Document data sources and any preprocessing steps

5. **Visualization**
   - Use appropriate chart types for the data being displayed
   - Add titles, labels, and legends to all plots
   - Ensure plots are readable and not overcrowded
   - Save important visualizations to files for reports

6. **Reproducibility**
   - Clear all outputs before committing to version control
   - Use seed values for random operations to ensure consistent results
   - Document the environment (Python version, key package versions)
   - Avoid hardcoding paths or values that might change

7. **Performance**
   - Use sampling for large datasets during development
   - Optimize code for performance when necessary
   - Avoid running cells that take excessive time without warnings
   - Use progress bars for long-running operations

8. **Documentation**
   - Add markdown cells explaining the purpose of each major code section
   - Include docstrings for custom functions defined in notebooks
   - Reference external documentation or sources when applicable
   - Update documentation when code changes

9. **Error Handling**
   - Include try-except blocks for operations that might fail
   - Provide informative error messages
   - Handle edge cases gracefully

10. **Version Control**
    - Commit notebooks with outputs cleared to avoid merge conflicts
    - Use meaningful commit messages
    - Consider using tools like nbstripout to automatically clean notebooks

## Project-Specific Guidelines

1. **File Organization**
   - Place all Jupyter notebooks in the `notebooks/` directory
   - Use descriptive filenames that reflect the notebook's purpose
   - Follow the project's naming conventions for notebooks

2. **Crime Data Analysis**
   - Follow the established data schema and column naming conventions
   - Use the project's utility functions from the analysis/ directory
   - Maintain consistency with existing analysis patterns

2. **Dashboard Integration**
   - Ensure notebook outputs are compatible with dashboard components
   - Use consistent styling and color schemes
   - Document any data transformations for dashboard use

3. **Reporting**
   - Generate reports in the reports/ directory following naming conventions
   - Include executive summaries and key findings
   - Use the project's reporting templates when available

## Notebook Execution

1. **Kernel Management**
   - Use the project's configured Python environment
   - Restart kernel when switching between major sections
   - Clear outputs regularly to maintain performance

2. **Cell Execution Order**
   - Ensure cells can be run in order without errors
   - Test execution from a fresh kernel state
   - Avoid dependencies on cells that must be run in a specific order

3. **Output Management**
   - Limit the size of cell outputs to prevent notebook bloat
   - Use print statements judiciously
   - Save large outputs to files when necessary

## Collaboration

1. **Code Reviews**
   - Ensure notebooks are readable by others
   - Add comments explaining complex analyses
   - Follow the project's coding standards

2. **Sharing**
   - Use nbviewer or similar for sharing notebooks
   - Convert to HTML/PDF for non-interactive sharing
   - Remove sensitive information before sharing

## Tools and Extensions

1. **Recommended Extensions**
   - Jupyter Notebook extensions for table of contents, code formatting
   - Use black or similar for code formatting
   - Enable spell checking for markdown cells

2. **Version Control Integration**
   - Use jupytext for text-based version control of notebooks
   - Consider git integration for collaborative work

## Agent Responsibilities

When creating, editing, or working with Jupyter notebooks, AI assistants are responsible for:

1. **Execution and Validation**
   - Run every cell in the notebook to ensure it executes without errors
   - Fix any bugs, syntax errors, or runtime issues encountered during execution
   - Verify that all code cells produce expected outputs

2. **Documentation and Explanation**
   - Provide clear explanations of the findings and results from each cell
   - Explain the importance of the data being analyzed
   - Describe any patterns or insights discovered in the data
   - Add markdown cells with detailed interpretations of results

3. **Quality Assurance**
   - Ensure notebooks are fully functional and reproducible
   - Document any assumptions, limitations, or caveats in the analysis
   - Validate that conclusions are supported by the data

4. **Project Maintenance**
   - Update the README file to reflect any new notebooks, changes, or findings
   - Commit all changes to version control with descriptive commit messages
   - Push changes to the remote repository to ensure they are shared with the team

Remember: These guidelines ensure that notebooks in this project are professional, maintainable, and contribute effectively to the Crime Incidents Philadelphia analysis.