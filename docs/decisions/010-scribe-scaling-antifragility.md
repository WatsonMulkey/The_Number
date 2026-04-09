# ADR 010: Scribe Scaling & Antifragility

**Status**: Accepted
**Date**: 2026-04-09
**Scope**: `~/.claude/scribe/` — extends [[ADR 009]] with scaling patterns, verification layers, and skill-authoring standards.

## Context

ADR 009 established the four-layer scribe structure (`raw/`, `compiled/`, `derived/`, plus existing `learnings/`, `sessions/`, `projects/`). That architecture handles current scale (~100 sessions, ~1600-line `patterns.md`, ~6 compiled articles, zero production pressure). This ADR captures what needs to exist *before* the scribe breaks under its own weight, not after.

Three inputs drove this ADR:

**1. The 2026-04-08 scrum-master + skeptic review** surfaced concrete scaling risks: `patterns.md` is already at 1600+ lines and growing, retrieval has no quality signal, there's no mechanism for detecting stale beliefs, and there's no way to tell if briefing token cost is degrading over time.

**2. Tran & Kiela 2026 ("Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets", Stanford)** reframed the "add more agents" instinct. Key findings relevant here:

- Under matched thinking-token budgets, within-family multi-agent decomposition loses information (Data Processing Inequality). Sequential and role-based MAS are *strictly worse* than single-agent at extraction tasks.
- Multi-agent only helps when single-agent context is actively corrupted (substitution, heavy masking) — not merely long or imperfect.
- The decisive success factor in both SAS and MAS is a **late constraint re-check** at finalization: surface a plausible candidate, then verify it against the original ask before output. Both systems' extraction failures come from losing a correct answer at finalization, not from reasoning errors.
- The paper is scope-bound: tested only on FRAMES and MuSiQue short-answer extraction with Qwen3, DeepSeek-R1-Distill, and Gemini 2.5. **It does not test cross-family multi-agent setups** and explicitly lists tools/vision/safety/long-form tasks as out of scope.

**3. Theo t3.gg's Opus vibe-drift critique** (2026-04-08 tweet): Claude Opus treats prompts as vibes, GPT/Codex treats them as instructions. The example — Opus recommending Bun as a JS runtime for Next.js even though Bun only works as a package manager there — is a concrete failure mode: pattern-matching on adjacent concepts rather than answering the literal question asked.

These three inputs converge on one prescription: **context quality is the load-bearing variable, and structural verification at the boundary beats architectural decomposition in the middle.** This ADR operationalizes that prescription as skill-authoring standards, a cross-family critic layer, and scaling mechanisms that protect retrieval quality as the scribe grows.

## Decision

### Guiding Principle: v1, Not v∞

This ADR captures a **starting point**, not a finished system. Every scaling mechanism below is scoped to what's needed now plus a clearly labeled next-review trigger. When a future model (Claude 5, or equivalent) is meaningfully better at literal instruction-following, revisit this ADR and decide what can be simplified or removed. Don't build infrastructure for problems we haven't hit.

### Skill-Authoring Standards

All scribe skills (existing and future) adopt three cross-cutting patterns.

#### 1. Pre-Analysis Scaffold (the "SAS-L" pattern)

Before starting mechanical work, every skill does a brief pre-analysis: restate the goal, identify ambiguities in this specific run, note how to resolve them, then begin. This is the "Longer Thinking" pattern from the Stanford paper (Qwen prompt D.1.2), which improved single-agent accuracy on Gemini without adding compute. Skill template block:

```markdown
## Before executing

1. Restate this skill's goal in your own words.
2. Identify any ambiguities in how it applies to this specific run.
3. Decide how you will resolve those ambiguities.
4. Only then begin Phase 1.
```

This is a free quality win — no infrastructure cost, no per-use friction.

#### 2. Late Constraint Re-Check

Every skill ends with an explicit verification step before producing its final output. Directly targets the Stanford paper's identified failure mode (correct answer surfaced mid-reasoning, lost at finalization) and Theo's vibe-drift critique (drift happens at output, not during reasoning). Skill template block:

```markdown
## Final: Answer-the-Asked-Question Check

Before outputting the final report/artifact, verify:
- Does this output answer what the skill was literally asked to produce?
- Does every claim trace to a specific mechanical check or cited source?
- Is there any content that drifted beyond the skill's scope?

Remove anything that fails. If the final output is shorter than you
expected, that's usually the check working correctly.
```

#### 3. Confidence-Gated User Prompts (three-tier pattern)

For mechanical checks on judgment-heavy data, classify each finding into three tiers:

- **HIGH CONFIDENCE** (meets all thresholds) → auto-include in report
- **BORDERLINE** (meets some thresholds) → pause, ask Watson with full inline context, proceed based on answer
- **LOW CONFIDENCE** (meets no thresholds) → drop silently

Constraints:

- **Hard cap**: max 5–8 borderline prompts per skill run. If more findings are borderline, prioritize by impact (active project > archived, error-dense > routine) and demote the excess to the low-confidence tier with a note in the final report.
- **Self-contained prompts**: every borderline prompt must include enough content from both sides (relevant file excerpts, not just references) that Watson can decide in under 10 seconds without opening anything.
- **Borderline is not approval**: a borderline prompt is for cases where only a human can decide. If the skill is already 90% sure, auto-include. Borderline tier is reserved for *"I genuinely don't know, your judgment is the input"*.

### Session Mode Declarations

Skills that require focused user attention (because of borderline prompts or complex decisions) declare a session mode in their frontmatter:

```yaml
session_mode: focused  # or "background" (default) / "quick"
attention_budget: "10-15 minutes, 3-8 borderline questions"
```

`/lint-knowledge` is `focused` mode. At invocation, it asks: *"Focused run (with borderline prompts) or quick run (auto-only, skip borderline)?"* Quick mode defers borderline findings to next focused run.

### Cross-Family Critic Layer

The "council" concept is narrowed and re-scoped based on the Stanford paper:

- **Within-family MAS is confirmed theater.** Parallel-roles, Sequential, Debate — all tested and all either match or underperform single-agent under matched budgets. A council of same-family Claude subagents (scrum-master, skeptic, architect) provides no real verification; they share priors and drift together.
- **Cross-family verification is the untested axis** — the Stanford paper couldn't speak to it. By elimination, it's the only multi-agent pattern with a plausible path to adding real value.
- **The critic is a checkpoint, not a generator.** It runs at deliberate boundaries (before committing an ADR, before publishing a compiled article, before closing a deep-work session), not inside every skill invocation.

#### Critic Architecture (v1)

- **Primary reviewer**: Qwen3-32B hybrid (lmstudio-community GGUF, Q5_K_M preferred) running locally via LM Studio at `http://localhost:1234/v1/chat/completions`. Configured in non-thinking mode (`/no_think` or equivalent directive in system prompt).
- **Why Qwen3 specifically**: Alibaba training corpus (distinctly different from Anthropic's), known strict instruction-following disposition (73.0 MultiIF), hybrid architecture supports both instruct and thinking modes from the same weights, April 2026 release.
- **Why not reasoning-tuned models** (QwQ, DeepSeek-R1 distills): the "circular reasoning" / over-exploration failure mode imports the exact problem we're defending against. Critic role needs *strict literalism*, not deep reasoning.
- **Invocation path**: skill writes artifact to a temporary file → bash `curl` to LM Studio's OpenAI-compatible endpoint → parses JSON response → returns to primary agent (Claude Code). No MCP bridge, no WSL2 boundary, no Hermes in the loop.
- **Config**: temperature 0.1–0.3 (literal, not creative), context 16K–32K, system prompt targets specific failure modes (see template below).
- **Fallback**: no fallback. If LM Studio isn't running, the skill fails loud and tells Watson to start it. No silent degradation.
- **Speed constraint**: none. Critic runs take 5–15 minutes and that's fine. It's only invoked at natural checkpoints.

#### Critic System Prompt (starting template)

```
You are a literalist reviewer. Your only job is to determine whether an
artifact actually answers the question it was asked to answer.

For each artifact you review:
1. Restate the original ask in your own words.
2. Identify every claim, decision, or recommendation the artifact makes.
3. Mark each one as either (a) directly answering the ask, (b) adjacent
   to the ask but not answering it, or (c) scope expansion beyond the ask.
4. Flag any ambiguities in the original ask that the artifact glossed over.
5. Output a structured review, not a narrative.

Do not be helpful. Do not soften criticism. Do not add suggestions
beyond what is needed to answer the literal question. If the artifact
answers the question, say so and stop.
```

Iterate on this prompt after practical use. The starting version targets Opus's known vibe-drift failure mode specifically.

#### Invocation Points (v1)

- Before committing any new ADR (`docs/decisions/*.md`)
- Before publishing any new compiled article (`compiled/*.md`) longer than ~200 lines
- Before closing a deep-work session via `session-end` (optional, Watson's call)

A `/council-review` skill wraps the bash-curl mechanics. Not built yet — write after ADR 010 lands.

### Scaling Mechanisms

#### Sub-File Chunking (patterns.md)

When `patterns.md` exceeds **2000 lines** (current: ~1600), split into `patterns-by-tag/{tag}.md` files, each covering one primary tag, with `patterns.md` becoming a tag index that points at the sub-files. Retrieval changes from "grep patterns.md for tag" to "read patterns-by-tag/{tag}.md directly."

**Trigger**: automatic proposal from `/lint-knowledge` when threshold is crossed. Watson approves the split. Manual if needed sooner.

**Defer**: the actual split implementation. Define the mechanism in this ADR; execute when threshold is crossed.

#### Article Index for /compile

`/compile` maintains `compiled/index.md` as an auto-updated TOC grouped by topic. Currently the index goes stale because nothing forces updates. Phase 5 of `/compile` will rewrite the index from the current state of `compiled/` every run — not append-only, but a full regenerate from the directory listing plus each file's frontmatter.

#### Briefing Token Cost Tripwires (Phase 0)

`session-start` logs briefing token cost to `.session-telemetry.md` (already implemented as of 2026-04-09). This ADR formalizes the three tripwires already documented in that file:

- Briefing > 60,000 tokens → add recency + relevance filtering
- Single project's context > 20,000 tokens → chunk sub-file retrieval
- "Why didn't you know X" moments > 3/week → retrieval is failing silently

When a tripwire fires, `session-start` surfaces a warning in the briefing. Watson decides whether to act or defer.

#### Query Logging (v1 minimal)

Each skill that reads scribe files appends one line per read to `~/.claude/scribe/.query-log.jsonl`:

```json
{"ts": "2026-04-09T12:34", "skill": "session-start", "action": "read", "path": "learnings/patterns.md", "bytes": 52341}
```

Purpose: diagnostic only. Enables "why didn't you know X" postmortems and provides raw data for future heat scoring. **Not implementing heat scoring yet** — log first, analyze later.

**Defer**: consuming the log. Build the consumer when there's enough data to tell if it's useful.

#### /compile 3+ Sources Rule

A new compiled article requires ≥3 distinct raw sources. 1–2 sources route to `learnings/` instead. Existing articles can be updated from a single new source — this rule only applies to NEW article creation. Enforced by `/compile` Phase 2 classification.

#### Contradiction Detection (v1 minimal)

`/lint-knowledge` Phase 5 (Gap Imputation) gains one additional check: for each pair of entries in `learnings/patterns.md` that share ≥2 tags, scan for negation patterns (one says "X works", another says "X doesn't work" or "avoid X"). Surface contradictions as borderline prompts — Watson decides which is current.

**Defer**: anything more sophisticated than tag-coincidence + negation grep. This is a dumb v1 mechanism deliberately.

#### Archival Policy (not deletion)

When `/lint-knowledge` identifies an entry as superseded, stale, or orphaned beyond rescue, it **moves** the entry to `~/.claude/scribe/archive/{layer}/` preserving the original path. Never deletes. Preserves audit trail. Archive is append-only and not indexed by default retrieval.

**Trigger**: proposed via borderline prompt in `/lint-knowledge`. Watson approves each archival.

#### Karpathy 400K Word Correction

ADR 009 referenced Karpathy's "~100 articles / ~400K words" claim as justification for rejecting vector DB / embeddings. **Corrected evidence**: the actual number in Karpathy's pattern was closer to ~100K words, not 400K. The decision to defer vector search is still correct (Claude can index ~100K words of compiled articles + tag-grepped learnings on demand without infrastructure), but the evidence base is ~4x smaller than ADR 009 documented. This ADR records the correction so future decisions aren't calibrated off a wrong number.

**Implication**: the vector DB rejection in ADR 009 has less headroom than previously thought. Revisit that decision when `compiled/` exceeds ~50K words or when retrieval starts missing relevant articles. Current state: well under threshold.

## Consequences

**Pro:**

- Three skill-authoring patterns (pre-analysis, late re-check, confidence-gated prompts) apply to *all* scribe skills including ones not yet written, giving compounding quality returns as the skill library grows.
- Cross-family critic layer provides an external verification check against Claude-specific drift modes (vibe interpretation, scope expansion, finalization loss) that no same-family reviewer can catch.
- Scaling mechanisms define *triggers* rather than pre-built systems, avoiding infrastructure for problems we haven't hit.
- Archival policy preserves audit trail, enabling recovery from bad `/lint-knowledge` decisions.
- Query logging creates diagnostic data for future retrieval improvements without requiring us to design the consumer now.
- Explicit v1 scope fence ("iterate later based on practical data") protects against over-engineering.

**Con:**

- Critic layer depends on LM Studio running locally. If Watson has LM Studio closed, `/council-review` fails. Low-blast-radius failure (skill fails loud, Watson starts LM Studio, retries), but it's a new dependency.
- Confidence-gated prompts require Watson's focused attention for `/lint-knowledge` runs. If he's not "locked in," the pattern produces sloppy data or gets rubber-stamped.
- Archival policy will grow the `archive/` folder unbounded. Deferred cleanup decision.
- Three-tier confidence pattern is untested in practice — the auto/borderline/drop thresholds may need retuning after first few runs.
- Qwen3-32B GGUF is ~20 GB download + ongoing disk usage. Already accepted as cost of the critic layer.
- Sub-file chunking for `patterns.md` changes how `capture-learning` writes new entries (target file depends on primary tag). Existing skill needs updating when split happens.

## Scope Boundaries

**Extends ADR 009**: four-layer structure stays as-is. This ADR adds patterns, verification, and scaling triggers on top. No changes to `raw/`, `compiled/`, `derived/`, `learnings/`, `sessions/`, `projects/` layout.

**What stays the same**:
- Obsidian as pure viewer, LLM writes all content
- Backlinks via `[[wiki-link]]` syntax
- `capture-learning`, `error-lessons`, `session-end` skill responsibilities
- Tag-based retrieval via grep for learnings

**What changes**:
- All skills adopt the three authoring patterns (pre-analysis, late re-check, confidence-gated where applicable)
- `/lint-knowledge` and `/compile` gain the patterns plus per-skill fixes (see Implementation Order)
- `session-start` gains tripwire warnings when telemetry crosses thresholds
- New `/council-review` skill for critic invocation
- New optional archive layer under `scribe/archive/`

## Not Doing (Yet)

- **Automatic sub-file chunking** — trigger-based, but Watson approves each split
- **Heat scoring / recency-weighted retrieval** — log queries first, design scoring later
- **Vector DB / embeddings** — reaffirmed deferred until grep + compiled index prove insufficient
- **Query log analysis / retrieval postmortem UI** — data collection only, no consumer yet
- **Cross-family critic automation via MCP bridge** — bash-curl MVP first; MCP bridge only if bash proves friction
- **Multi-critic councils** (Qwen + Mistral + Gemma etc.) — start with one critic; add second family only if single critic proves insufficient
- **Contradiction detection beyond tag-coincidence + negation grep** — sophisticated NLI-style checking deferred
- **Retrofitting audit findings from `/lint-knowledge` and `/compile`** — those per-skill fixes (confidence-gated duplicate detection, 3+ sources rule, verification phase, grounding check) land as a follow-up cleanup ticket after ADR 010 ships
- **Automatic invocation of the critic** on every artifact — deliberate invocation only in v1
- **Back-pressure from tripwires to retrieval** — tripwires surface warnings, don't auto-filter

When the first of these hurts enough to warrant building, file a new ADR or extend this one.

## Implementation Order

1. **Commit this ADR** as `docs/decisions/010-scribe-scaling-antifragility.md`
2. **Download Qwen3-32B GGUF Q5_K_M** via LM Studio (in progress as of 2026-04-09)
3. **Smoke-test the critic** by running the system prompt against a sample ADR (this one works as a first test — "does this ADR answer what it was asked?")
4. **Write `/council-review` skill** wrapping bash-curl → LM Studio with the starting system prompt
5. **Update `session-start` to surface tripwire warnings** when `.session-telemetry.md` thresholds are crossed
6. **Add query logging to `session-start`, `session-end`, `/lint-knowledge`, `/compile`** — one-line JSONL append per scribe file read
7. **Update `/lint-knowledge`** with: pre-analysis scaffold, late constraint re-check, confidence-gated three-tier (backlinks + duplicate detection + contradiction detection + gap imputation), session-mode declaration, archival policy proposals
8. **Update `/compile`** with: pre-analysis scaffold, late constraint re-check, 3+ sources rule, source grounding check (Phase 4.5), classification threshold literals
9. **Update `session-start` and `session-end`** with pre-analysis scaffold + late constraint re-check on open-ended steps (briefing generation, handoff writing)
10. **Linear tickets**: FOI team, "Knowledge Base" label, one ticket per implementation step
11. **First focused `/lint-knowledge` run** using the new three-tier pattern — this is the first practical test of whether the confidence thresholds need tuning
12. **Retrospective after 2 weeks of practical use** — what worked, what drifted, what needs iteration

## References

- [[ADR 009]] — LLM Knowledge Base Architecture (foundation this extends)
- Tran, D. & Kiela, D. (2026). *Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets.* arXiv:2604.02460. Stanford.
- Theo t3.gg (2026-04-08). Opus vibe-drift critique, Twitter/X. Archived to `raw/prompts/2026-04-08_theo-opus-vibes.md`.
- 2026-04-08 scrum-master + skeptic review session — original punch list (`[[sessions/2026-04-08_knowledge-base-architecture-rollout]]`)
- Qwen3 release announcement (2026-04-29) — [qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/)
- [[patterns#Related Knowledge Section in Project HANDOFFs]] — curated cross-project relevance pattern, applied here
- [[insights#Self-Improving Knowledge Bases Need Historical Retrofit]] — Phase 6b reasoning referenced in `/lint-knowledge`
