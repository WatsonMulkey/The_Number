---
name: capture-learning
description: Capture a significant learning, pattern, or insight mid-session. Use when something worth remembering happens — replaces supermemory as the institutional memory system.
---

# Capture Learning

Store learnings, patterns, and insights in the local scribe system for retrieval across future sessions. This is Watson's institutional memory — treat it as permanent knowledge infrastructure.

## When to Use This Skill

**Use immediately when:**
- You discover a non-obvious technical pattern (e.g., "plugout~ defaults to mono")
- An error is resolved and the root cause is worth remembering
- A process or workflow insight emerges (e.g., "mock-first for copy iteration works")
- Watson says "remember this" or "we should remember that"
- A tool/library has an undocumented gotcha
- An architectural decision is made with important rationale

**Do NOT use for:**
- Session-specific context (current task details, temporary state)
- Information that's already in a CLAUDE.md or ADR
- Obvious/well-documented behavior (e.g., "Python uses indentation")

## Instructions

### 1. Classify the learning

Determine which file it belongs in:

| Type | File | Examples |
|------|------|----------|
| **Pattern** | `~/.claude/scribe/learnings/patterns.md` | Architectural patterns, code patterns, workflow patterns, tool usage patterns |
| **Error** | `~/.claude/scribe/learnings/errors.md` | Error resolutions, debugging insights, failure modes |
| **Insight** | `~/.claude/scribe/learnings/insights.md` | Process realizations, strategic observations, meta-learnings |

### 2. Check for duplicates

Search the target file before writing:
```
Grep pattern="[key phrase from learning]" path="~/.claude/scribe/learnings/[file].md"
```

If a similar entry exists, **update it** (add new context, date, or examples) rather than creating a duplicate.

### 3. Append the learning

Use the established format for the target file. Each file uses the same structure:

```markdown
---

### [Descriptive, searchable title]
**Date**: YYYY-MM-DD
**Project**: [project-name or "general"]
**Context**: [One sentence on what prompted this learning]

**Learning**:
[The core insight — what did you learn? Be specific and actionable.]

**Application**:
- [When/how to apply this in the future]
- [Concrete guidance, not vague advice]

**Tags**: #domain #project #specific-tool #category
```

### 4. Tag discipline

Always include tags from these categories:
- **Project**: `#the-number`, `#foil-engineering`, `#resume-tailor`, `#rag-vault`, `#buyer-mode`, `#mixdiff`, `#audio-scribe`, `#sample-vault`
- **Domain**: `#max-for-live`, `#astro`, `#vue`, `#python`, `#typescript`, `#prisma`, `#windows`, `#git`, `#deployment`
- **Type**: `#architecture`, `#security`, `#testing`, `#workflow`, `#over-engineering`, `#silent-failure`, `#data-loss`, `#ui`, `#css`

If introducing a new tag that doesn't appear in the patterns.md Tag Index, add it to the appropriate category in the index.

### 5. Confirm

Report back:
```
Learning captured: [Title]
  -> [patterns|errors|insights].md
  -> Tags: #tag1 #tag2 #tag3
```

## Storage Architecture

All institutional memory lives in `~/.claude/scribe/learnings/`:

```
learnings/
  patterns.md    — HOW things work (code, architecture, tools)
  errors.md      — WHAT went wrong and how to fix it
  insights.md    — WHY things work the way they do (process, strategy)
```

These files are searched via Grep by the `retro` skill before major decisions. The tag index at the top of `patterns.md` enables fast, targeted retrieval without reading the full file.

## Integration

- **retro** skill searches these files before planning/orchestration
- **error-lessons** skill writes to `errors.md` specifically
- **session-end** skill may reference recent learnings in handoff notes
- MEMORY.md (auto-loaded) contains permanent preferences — learnings go HERE, not there
