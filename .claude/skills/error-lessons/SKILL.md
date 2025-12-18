---
name: error-lessons
description: Automatically capture and document lessons from any error encountered during development. Use immediately when you or any agent encounters an error to create institutional knowledge and prevent future occurrences.
---

# Error Lessons

ANYTIME you or any agent encounters an error, use this skill to capture and document the lesson. This builds institutional knowledge to prevent repeating mistakes and helps diagnose similar issues faster.

## When to Use This Skill

**REQUIRED immediately after:**
- Any error message appears (compilation, runtime, API, dependency, etc.)
- A tool fails or returns an error
- An agent encounters a problem during execution
- A build/test/deployment fails
- Configuration issues arise
- Integration problems occur

**Use for ALL error types:**
- Syntax errors
- Runtime errors
- API errors
- Dependency/installation errors
- Configuration errors
- Git/version control errors
- Tool-specific errors
- Integration errors

## Instructions

### 1. Check for Existing Lesson

Before creating a new lesson, search supermemory to avoid duplicates:

```
Search supermemory for: "[error type] [key error message text]"
```

Examples:
- "Unknown skill retro"
- "WeasyPrint Cairo dependency Windows"
- "CORS configuration FastAPI"
- "Git embedded repository warning"

**If a lesson exists:** Update it with new context or skip if identical.

**If no lesson exists:** Proceed to create a new lesson.

### 2. Capture Error Details

Document the following information:

**Error Signature:**
- Error type/category (e.g., "Skill Loading Error", "Dependency Error", "Git Warning")
- Exact error message or key excerpt
- Tool/system that generated the error
- Context where it occurred

**How It Shows Up:**
- What action triggered the error?
- What were you trying to accomplish?
- What symptoms appeared?
- Any related warnings or messages?

**Why It's Important:**
- What functionality breaks?
- What user impact occurs?
- What development friction does it cause?
- What are the downstream consequences?

**Root Cause:**
- What is the underlying issue?
- What assumption or configuration was wrong?
- What was misunderstood about the system?

**How to Fix:**
- Step-by-step resolution
- Specific commands or code changes
- Configuration adjustments needed
- Prevention strategies

**Related Context:**
- Links to documentation
- Related errors or issues
- Dependencies involved
- Version/environment specifics

### 3. Store Lesson in Supermemory

Use a consistent format for easy retrieval:

```
Error Lesson: [Error Type]

Signature: [Exact error message or key excerpt]

Trigger: [What action caused it]

Impact: [Why it matters]

Root Cause: [Underlying issue]

Fix: [How to resolve]
- Step 1
- Step 2
- Step 3

Prevention: [How to avoid in future]

Context: [Tool versions, environment, related info]

Tags: #error #[category] #[tool-name]
```

### 4. Add to BEST_PRACTICES.md (If Applicable)

For common or important errors, consider adding to the "Common Pitfalls" section of BEST_PRACTICES.md to make them more discoverable.

## Output Format

Provide a brief confirmation:

```
✅ Error lesson captured: [Error Type]
- Stored in supermemory with tags: #error #[category]
- [Added to BEST_PRACTICES.md / Skipped - duplicate found]
```

## Examples

### Example 1: Skill Loading Error

```
Error Lesson: Claude Code Skill Loading Failure

Signature: "Unknown skill: retro"

Trigger: Attempted to invoke skill with /skill retro after creating .claude/skills/retro.md

Impact: Skills cannot be used, reducing development efficiency and breaking workflow automation

Root Cause: Skills must be in directory structure (.claude/skills/skill-name/SKILL.md) not flat files (.claude/skills/skill-name.md)

Fix:
- Create directory: mkdir .claude/skills/retro/
- Move content to: .claude/skills/retro/SKILL.md
- Add YAML frontmatter with name and description fields
- Restart Claude Code to reload skills

Prevention: Always create skills as directories with SKILL.md inside. Check Claude Code documentation before creating custom skills.

Context: Claude Code skill discovery mechanism, Windows environment

Tags: #error #skill-loading #claude-code #directory-structure
```

### Example 2: Git Embedded Repository

```
Error Lesson: Git Embedded Repository Warning

Signature: "warning: adding embedded git repository: resume-tailor"

Trigger: Running git add on a directory that contains its own .git folder

Impact: Submodule not properly configured, outer repo won't track inner repo changes, clones will be incomplete

Root Cause: Added a git repository inside another git repository without using git submodule

Fix:
- Remove from staging: git rm --cached resume-tailor
- Either: Use git submodule add <url> resume-tailor
- Or: Remove inner .git folder if not needed as separate repo

Prevention: Use git submodule for nested repositories. Check for .git folders before adding directories.

Context: Git version control, repository management

Tags: #error #git #submodule #repository-structure
```

### Example 3: Dependency Error

```
Error Lesson: WeasyPrint Windows Installation Failure

Signature: "cairo library not found" or "Failed to load cairo DLL"

Trigger: pip install weasyprint on Windows

Impact: PDF generation fails, blocking resume output functionality

Root Cause: WeasyPrint requires Cairo, Pango, and GDK-PixBuf native libraries which are problematic on Windows

Fix:
- Install GTK+ runtime for Windows
- Or: Use alternative library (ReportLab - pure Python)
- Or: Use Docker with Linux base image

Prevention: Check library dependencies for Windows compatibility before choosing. Prefer pure Python libraries for cross-platform projects.

Context: Windows 10/11, Python PDF generation, WeasyPrint vs ReportLab

Tags: #error #dependency #windows #weasyprint #cairo
```

## Integration with Other Skills

This skill works alongside:
- **retro**: Error lessons inform retrospective learning
- **best-practices-review**: Documented errors become best practice pitfalls
- All agents: Any agent that encounters errors should trigger this skill

## Anti-Patterns to Avoid

❌ **Don't:**
- Skip documenting "small" or "obvious" errors
- Create vague lessons without specific error messages
- Forget to check for duplicates
- Leave out the fix/prevention steps
- Use inconsistent formatting

✅ **Do:**
- Document every error, even if resolution was quick
- Include exact error messages for searchability
- Check supermemory before creating new lessons
- Provide step-by-step fixes
- Use consistent tagging for categorization

## Success Metrics

A good error lesson should:
- Allow someone to identify the same error immediately
- Provide enough context to understand why it matters
- Give clear, actionable fix steps
- Prevent the error from recurring
- Be discoverable through search (good tags/keywords)
