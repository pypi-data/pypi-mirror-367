# OBK Feature Workflow



## Overview

The OBK Feature Workflow is a standardized process for introducing new features to the OBK project mainline.
It emphasizes clarity, testability, agent-driven automation, and reproducible history—enabling teams to move quickly, learn efficiently, and minimize surprises as the project evolves.

This workflow incorporates best practices from test-driven development (TDD), prompt-driven development, and consistent agent handoff. It is designed to integrate seamlessly with Codex, GSL, and future automation tools.



## Step-by-Step Workflow

1. **Write an Article for the Feature**
    
    * Describe the feature you want to integrate.
        
    * File the article in your working branch, organizing articles between `todo`, `doing`, `done`, or subfolders as needed.
        
2. **Start a Feature Branch**
    
    * Name: `feature/short-description`
        
    * `pull` from `main` first to ensure you’re up to date.
        
3. **Add the Article to Your Feature Branch**
    
    * Complete any housekeeping, keeping your articles organized.
        
4. **Start a Codex Automation Branch from the Feature Branch**
    
    * Name: `codex-automation/short-description`
        
5. **Create a New Prompt File Using the Prompt Template**
    
    * Duplicate [Prompt Template for Codex Agents](prompt-template-for-codex-agents.md).
        
    * Fill out all template sections:
        
        * Description
            
        * Purpose
            
        * Inputs
            
        * Outputs
            
        * Workflows
            
        * Tests (`<gsl-tdd>`)
            
        * Document specification
            
6. **Draft One-Line Manual Tests in the Prompt**
    
    * Write shell/REPL one-liners or CLI commands that represent desired behaviors or edge cases.
        
    * Add these to the `<gsl-tdd>` section of your prompt file.
        
    * See [Why One-Line Manual Tests Should Precede Automation](one-line-manual-tests.md) for rationale and examples.
        
7. **Write an Ad-Hoc Task for Codex Using the Adhoc Task Template**
    
    * Use [Adhoc Task Template for Codex Agents](adhoc-task-template-for-codex-agents.md).
        
    * Reference your prompt’s `<gsl-tdd>` section and feature article.
        
    * Specify allowed and prohibited modifications, and clearly define step-by-step agent actions.
        
8. **Send the Directive in Codex Chat**
    
    * “Execute directives in task [task-file-name]” via Codex.
        
9. **Review Generated Code Possibilities**
    
    * Codex may generate up to 4 options per run.
        
    * Optionally analyze pros/cons in ChatGPT.
        
    * Pick the best version for integration.
        
10. **Create a PR with the Chosen Code**
    
    * Merge changes back to `codex-automation/short-description`.
        
11. **Start a Codex Cross-Review Branch**
    
    * Name: `codex-cross-review/short-description`
        
    * Base it on `codex-automation/short-description`.
        
12. **Iterate on Testing**
    
    * Run `pytest`.
        
    * Perform manual tests (as defined in `<gsl-tdd>`).
        
    * Convert stable manual tests to automated (pytest) tests where possible.
        
13. **Final Review of Prompt and Work**
    
    * Ensure the `<gsl-tdd>` section contains all relevant manual and automated tests.
        
    * Confirm your prompt file fully adheres to the [Prompt Template](prompt-template-for-codex-agents.md) and [Document Specification](prompt-template-for-codex-agents.md#document-specification):
        
        * Unique test IDs
            
        * Clear agent/human edit boundaries
            
        * All required sections present and clear
            
14. **Merge Back to codex-automation/short-description**
    
15. **Merge codex-automation/short-description to feature/short-description & Push**
    
16. **Open a PR from feature/short-description to main**
    
    * **Do NOT use `[deploy]` in the commit message.**
        
    * Pull to local as needed to keep up to date.
        
    
    > **NOTE:**  
    > Only PRs with `[deploy]` in the squash-merge commit message will trigger a deploy to PyPI via CI/CD.  
    > **Normal feature merges should NOT include `[deploy]`.**
    



## Best Practices

* **Manual, one-line tests come first:**  
    Prove value manually, then automate.
    
* **Use the Prompt and Ad-Hoc Task Templates:**  
    Every Codex/feature task should be fully templated for clarity and consistency.
    
* **Follow the prompt document specification:**  
    Unique IDs, agent vs. human edit boundaries, and section requirements are strictly enforced.
    
* **Maintain branch naming consistency:**  
    For feature, Codex automation, and cross-review branches.
    



## References

* [Prompt Template for Codex Agents](prompt-template-for-codex-agents.md)
    
* [Why One-Line Manual Tests Should Precede Automation](one-line-manual-tests.md)
    
* [Adhoc Task Template for Codex Agents](adhoc-task-template-for-codex-agents.md)
    

* * *