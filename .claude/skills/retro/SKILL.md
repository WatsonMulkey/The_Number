---
name: retro
description: Review past sessions and learnings to improve current task execution. Use before creating implementation plans, orchestrating agents, or making architectural decisions.
---

# Retrospective Learning

Before creating plans or orchestrating agents, review past sessions to learn from missteps, errors, and what worked well. This ensures continuous improvement and better collaboration.

## When to Use This Skill

**REQUIRED before:**
- Creating implementation plans
- Orchestrating multiple agents
- Starting significant new features
- Making architectural decisions

**OPTIONAL for:**
- Small bug fixes
- Single-agent tasks
- Routine maintenance

## Instructions

### 1. Search local scribe learnings by tag/keyword

The primary knowledge base is in `~/.claude/scribe/learnings/`. These files are large — **do NOT read them in full**. Use Grep to search by tag or keyword.

**Files:**
- `patterns.md` — Architectural and process patterns (tagged, indexed)
- `errors.md` — Error patterns and solutions (tagged)
- `insights.md` — General insights and realizations (tagged)

**How to search:** Use Grep with the tag or keyword most relevant to your current task:
```
Grep pattern="#max-for-live" path="~/.claude/scribe/learnings/patterns.md"
Grep pattern="#deployment|#vercel" path="~/.claude/scribe/learnings/errors.md"
Grep pattern="resume-tailor" path="~/.claude/scribe/learnings/"
```

Then read the surrounding context (use -B 5 -A 20) for any matches to get the full pattern.

**Common tags in the learnings files:**
- Projects: `#the-number`, `#foil-industries`, `#resume-tailor`, `#rag-vault`, `#buyer-mode`, `#mixdiff`, `#audio-scribe`
- Domains: `#max-for-live`, `#astro`, `#prisma`, `#security`, `#windows`, `#sqlite`, `#css`
- Types: `#deployment`, `#over-engineering`, `#silent-failure`, `#data-loss`, `#validation`
- Process: `#testing`, `#code-review`, `#multi-agent-review`, `#refactoring`

### 2. Check the scribe session index for recent context

Scan `~/.claude/scribe/index.md` for sessions related to the current task. The index has one-line summaries — only read the full session handoff if a summary looks directly relevant.

### 3. Review recent conversation history for:
- Similar tasks attempted previously
- Agent collaboration patterns that succeeded or failed
- User feedback on past approaches

### 4. Supplement with supermemory (if available)

Supermemory may have additional context not in local files. Search it for the current task type, but treat local scribe files as the authoritative source.

### 5. Apply learnings to current task:
- Adjust scope based on past feedback
- Avoid documented anti-patterns
- Use proven approaches that worked
- Set realistic timelines based on history

### 6. Document new learnings after task completion:
- Append to the appropriate local scribe file (`patterns.md`, `errors.md`, or `insights.md`)
- Use the established format: `### Title`, `**Date**`, `**Project**`, `**Context**`, body, `**Tags**: #tag1 #tag2`
- Optionally mirror to supermemory

## Output Format

Provide a concise summary (3-5 bullet points) of:
- **Past mistakes to avoid** (e.g., "6-week timeline was rejected as over-engineered")
- **Proven approaches to use** (e.g., "User prefers lean MVP with sample output for review")
- **User preferences identified** (e.g., "Prioritizes quality over speed")
- **Technical decisions that worked/failed** (e.g., "WeasyPrint rejected due to Windows dependencies")

## Example

**For a new API design task:**
- Search: `Grep pattern="#deployment|#the-number" path="~/.claude/scribe/learnings/errors.md"`
- Found: Vercel project confusion pattern — always verify `.vercel/project.json` before deploying
- Found: SQLite defaults aren't production-ready — enable WAL mode for multi-user
- Apply: Verify deployment target before starting, configure DB for concurrent access upfront

## Integration with Other Skills

This skill should run BEFORE:
- `/skill best-practices-review` - General best practices
- Agent orchestration - Apply lessons to agent selection and coordination
- Planning sessions - Inform scope and timeline decisions

Keep the retro brief and actionable - focus on what directly impacts the current task.
