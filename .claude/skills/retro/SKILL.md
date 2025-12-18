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

1. **Search supermemory for relevant learnings** related to:
   - The current task type (e.g., "PDF generation", "testing strategy", "API design")
   - Past mistakes or anti-patterns documented
   - Successful approaches that worked well

2. **Review recent conversation history** for:
   - Similar tasks attempted previously
   - Agent collaboration patterns that succeeded or failed
   - User feedback on past approaches

3. **Extract key lessons** such as:
   - What was over-engineered or under-scoped?
   - Which agent recommendations were accepted vs rejected?
   - What timelines were realistic vs inflated?
   - Which dependencies or tools caused problems?
   - What did the user actually value vs what we assumed?

4. **Apply learnings to current task:**
   - Adjust scope based on past feedback
   - Avoid documented anti-patterns
   - Use proven approaches that worked
   - Set realistic timelines based on history

5. **Document new learnings** after task completion:
   - Store what worked well in supermemory
   - Document what didn't work and why
   - Update best practices if applicable

## Output Format

Provide a concise summary (3-5 bullet points) of:
- **Past mistakes to avoid** (e.g., "6-week timeline was rejected as over-engineered")
- **Proven approaches to use** (e.g., "User prefers lean MVP with sample output for review")
- **User preferences identified** (e.g., "Prioritizes quality over speed")
- **Technical decisions that worked/failed** (e.g., "WeasyPrint rejected due to Windows dependencies")

## Example

**For a new API design task:**
- ✗ Avoid: Building multiple endpoints before validating one works
- ✓ Use: FastAPI with encrypted database (proven in backend)
- 👤 User prefers: Seeing working examples before committing to approach
- 🔧 Technical: CORS configuration caused issues - document settings upfront

## Integration with Other Skills

This skill should run BEFORE:
- `/skill best-practices-review` - General best practices
- Agent orchestration - Apply lessons to agent selection and coordination
- Planning sessions - Inform scope and timeline decisions

Keep the retro brief and actionable - focus on what directly impacts the current task.
