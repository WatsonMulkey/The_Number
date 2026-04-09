# ADR 009: LLM Knowledge Base Architecture

**Status**: Accepted
**Date**: 2026-04-08
**Scope**: `~/.claude/scribe/` — Watson's institutional memory / knowledge base (user-level, global across all projects)

## Context

Watson's current persistence stack is a patchwork of markdown files that Claude writes and rarely reads in full:

- `~/.claude/projects/{cwd}/memory/` — auto-memory (user/feedback/project/reference files, indexed by `MEMORY.md`)
- `~/.claude/scribe/learnings/` — patterns, errors, insights (tag-indexed)
- `~/.claude/scribe/sessions/` — per-session logs
- `~/.claude/scribe/projects/` — per-project handoff docs
- `~/Dev/docs/decisions/` — project-level ADRs
- `~/Dev/docs/BEST_PRACTICES.md` — cross-project guidelines

This system works — sessions already file back into it via `session-end`, `capture-learning`, and `error-lessons` skills. Claude is the primary writer; Watson rarely edits these files directly.

Karpathy's "LLM Knowledge Base" pattern (screenshots, 2026-04-08) describes a close cousin of what Watson has already been building, with a few architectural refinements worth adopting:

1. **Explicit `raw/` layer** — source material (articles, research, prompts) distinct from derived/synthesized knowledge, enabling re-compilation as understanding improves.
2. **LLM "linting"** — periodic health checks over the wiki that find stale references, duplicate entries, missing connections, and impute gaps. Watson's memory rules already warn "Before recommending from memory, verify current state" — this formalizes that check as a skill.
3. **Obsidian as pure viewer** — LLM owns all writes; human reads via graph view, backlinks, full-text search, Marp slide rendering. Zero code.
4. **Render-and-refile** — session outputs (slides, charts, analyses) file back into the knowledge base as new sources.
5. **Backlinks** — explicit `[[wiki-link]]` syntax between sessions, learnings, project memories, and ADRs creates a navigable graph.

The gap between Watson's current system and Karpathy's is structural, not conceptual. This ADR captures the refinement.

## Decision

### Four-layer Scribe Structure

```
~/.claude/scribe/
├── raw/                  # NEW — ingested source material, untouched
│   ├── articles/         # clipped web articles (Obsidian Web Clipper → .md)
│   ├── research/         # competitive/client/technical research
│   ├── prompts/          # interesting prompts, patterns, LLM outputs to riff on
│   └── images/           # screenshots, diagrams, reference visuals
├── compiled/             # NEW — LLM-synthesized concept articles with backlinks
│   └── {concept}.md      # e.g., `vector-databases.md`, `vercel-fluid-compute.md`
├── derived/              # NEW — rendered visual outputs
│   ├── slides/           # Marp slide decks from retros + session summaries
│   └── charts/           # matplotlib/SVG from analyses
├── learnings/            # EXISTING — patterns/errors/insights (LLM-maintained tag index)
├── sessions/             # EXISTING — per-session logs
├── projects/             # EXISTING — per-project HANDOFF.md + LEARNINGS.md
└── index.md              # EXISTING — session index, auto-maintained
```

**Rationale**: The existing `learnings/`, `sessions/`, `projects/` directories already work and don't need to move. The new `raw/`, `compiled/`, `derived/` layers add capabilities that the current system can't express: source auditability, concept-level indexing, and visual output persistence.

### LLM Writes, Human Reads

Reaffirmed as an explicit principle. Watson should almost never hand-edit files in `scribe/`. Claude writes via skills:

- `capture-learning` → `learnings/*.md`
- `error-lessons` → `learnings/errors.md`
- `session-end` → `sessions/*.md`, `projects/*/HANDOFF.md`, `index.md`
- `lint-knowledge` (NEW) → fixes stale entries, adds missing backlinks, suggests new articles
- `compile` (NEW) → reads `raw/` and writes `compiled/*.md`

The only exception: Watson may drop source material into `raw/` manually (via Web Clipper hotkey, drag-and-drop, or save-as). The LLM picks it up on next `/compile`.

### Obsidian as the Frontend

Open `~/.claude/scribe/` as an Obsidian vault. Zero build, zero config. Benefits:

- Graph view over the entire knowledge base
- Backlinks rendered automatically from `[[wiki-link]]` syntax
- Full-text search across all markdown
- Marp community plugin renders `derived/slides/*.md` as slide decks
- Obsidian Web Clipper extension auto-saves captured articles to `raw/articles/`

**Rejected alternative**: Custom UI / web app. Would take weeks to build for capabilities Obsidian already provides.

### Backlinks via Obsidian `[[wiki-link]]` Syntax

When Claude writes session logs, learnings, handoffs, or compiled articles, it uses Obsidian-compatible `[[link]]` syntax to reference other notes. Example:

```markdown
## Session Summary
Fixed 5 Drew beta bugs in [[the-number]]. Related: [[FOI-109]], [[FOI-110]]...
See learnings: [[patterns#Vuetify tag nav breaks routing]].
```

This creates a navigable graph with zero tooling changes. Backlinks are maintained by Claude on write; `/lint-knowledge` adds missing ones retroactively.

**Retrofit strategy**: Don't mass-edit existing files. Let backlinks accumulate organically in new sessions, plus `/lint-knowledge` can propose backlink additions during its health check.

### LLM Linting as a First-Class Skill

`/lint-knowledge` runs on-demand (weekly or ad-hoc) and:

1. **Stale reference check** — grep `MEMORY.md` + learnings for file/function/flag references; verify they still exist in the referenced codebase
2. **Duplicate detection** — semantic dedup of similar entries in `patterns.md`, `errors.md`, `insights.md`
3. **Orphan detection** — sessions with no project handoff, memories with no backlinks, handoffs referencing closed Linear tickets
4. **Gap imputation** — sessions missing learnings that obviously should exist (errors encountered but no entry in `errors.md`)
5. **Connection suggestions** — pairs of sessions/learnings that share topics but aren't linked
6. **New article candidates** — concepts referenced ≥3 times across the knowledge base without a compiled article

Output: a structured report. Watson approves changes; Claude applies them.

### Compile Skill for Raw → Compiled

`/compile` runs on-demand (end of a research-heavy session) and:

1. Lists unprocessed files in `scribe/raw/` (any file modified since last `/compile` timestamp)
2. For each new source, determines: append to existing `compiled/*.md` article? Create new article? File as learning? Ignore?
3. Writes compiled article(s) with:
   - Frontmatter pointing back to source file(s) in `raw/`
   - `[[backlinks]]` to related concepts
   - Tag suffix for the learnings search pattern
4. Updates a `compiled/index.md` auto-maintained TOC

**Rationale**: At Karpathy's described ~100 articles / ~400K word scale, Claude can read `compiled/index.md` + a few related articles on demand. No vector DB, no embeddings. Keep it simple until it fails.

## Consequences

**Pro:**
- Source auditability — if a learning turns out to be wrong, we can re-read the original `raw/` source
- Zero-cost visual frontend via Obsidian — no custom UI to maintain
- LLM-linted knowledge base catches stale references automatically, addressing the existing warning in `MEMORY.md` about verifying state before recommending
- Backlinks create navigable graph without schema/tooling changes
- Render-and-refile loop means session outputs compound instead of evaporating

**Con:**
- Another skill to maintain (`/lint-knowledge`, `/compile`)
- Claude must learn to write `[[wiki-link]]` syntax consistently — will require prompt reinforcement in skills
- `raw/` layer will grow unbounded unless we add archival policy (deferred)
- Linter could generate noise if thresholds aren't tuned — first runs may surface dozens of "issues" that are really fine
- `compiled/` duplicates information already in `learnings/` — need clear guidance on what goes where (see below)

### Scope Boundaries — What Goes Where

| Content type | Home | Written by |
|---|---|---|
| Unprocessed article / research doc | `raw/articles/` | Watson (Web Clipper) or Claude (save-as) |
| Pattern (HOW something works) | `learnings/patterns.md` | `capture-learning` skill |
| Error + fix | `learnings/errors.md` | `error-lessons` skill |
| Insight (WHY something works) | `learnings/insights.md` | `capture-learning` skill |
| Concept article (multi-source synthesis) | `compiled/{concept}.md` | `/compile` skill |
| Session log | `sessions/{session-id}.md` | `session-end` skill |
| Project handoff | `projects/{project}/HANDOFF.md` | `session-end` skill |
| ADR | `~/Dev/docs/decisions/` | Watson + Claude (collaborative) |
| Slide deck from retro | `derived/slides/{topic}.md` (Marp) | `session-end` or `/retro` skill |
| Chart from analysis | `derived/charts/{topic}.{svg,png}` | ad-hoc skill (future) |

**Rule**: `learnings/*` is for atomic facts (3-10 lines). `compiled/*` is for multi-source articles (hundreds of lines). If you can't decide, it probably goes in `learnings/`.

### Not Doing (Yet)

- **Custom scribe CLI** — deferred. Grep-by-tag already works. Add only if Hermes or other external agents need scribe access.
- **Synthetic data / fine-tuning** — deferred to backlog. Not urgent at current scale.
- **Vector DB / embedding search** — rejected until grep + Obsidian search proves insufficient. Karpathy's evidence suggests "~100 articles / ~400K words" is well within what LLMs can index themselves.
- **Mass backlink retrofit** — let backlinks accumulate organically. `/lint-knowledge` proposes adds.
- **Image deduplication / OCR over `raw/images/`** — deferred.

## Implementation Order

1. Create `raw/`, `compiled/`, `derived/` subdirectories with READMEs
2. Write `/lint-knowledge` skill (user level)
3. Write `/compile` skill (user level)
4. Enhance `session-end` skill with render-and-refile + backlink stubs
5. Document Obsidian vault + Web Clipper setup
6. Run `/lint-knowledge` smoke test against current state
7. Linear tickets: FOI team, new "Knowledge Base" label

## References

- Karpathy's LLM Knowledge Base pattern (screenshots, 2026-04-08)
- `~/.claude/projects/C--Users-watso-Dev/memory/MEMORY.md` — existing memory index
- `~/.claude/scribe/index.md` — existing session index
- `~/Dev/docs/decisions/007-mcp-bridge-strategy.md` — prior meta-architecture ADR
