#!/bin/bash
# Session End Hook - Updates context for next session
# This can be called manually or integrated with Ralph Wiggum stop-hook

set -e

echo "═══════════════════════════════════════════════════════════"
echo "         Session End - Capturing Context"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 1. Get session summary
echo "📝 What was accomplished this session?"
echo "   (Brief summary for next session handoff)"
echo ""
echo "> "
read -r SESSION_SUMMARY

# 2. Update deployment status if anything was deployed
echo ""
echo "🚀 Was anything deployed? (y/n)"
read -r DEPLOYED

if [ "$DEPLOYED" = "y" ] || [ "$DEPLOYED" = "Y" ]; then
    echo "   What was deployed? (frontend/backend/both)"
    read -r DEPLOY_TARGET

    echo "   ⚠️  REMINDER: Update docs/DEPLOYMENT_STATUS.md manually with:"
    echo "      - Timestamp"
    echo "      - Commit hash"
    echo "      - What changed"
    echo "      - Testing results"
fi

# 3. Check for uncommitted changes
UNCOMMITTED=$(git status --short | wc -l)
if [ "$UNCOMMITTED" != "0" ]; then
    echo ""
    echo "⚠️  WARNING: You have $UNCOMMITTED uncommitted changes"
    echo "   Consider committing before ending session"
fi

# 4. Check commits not pushed
UNPUSHED=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$UNPUSHED" != "0" ]; then
    echo ""
    echo "⚠️  You have $UNPUSHED commits not pushed to origin"
fi

# 5. Save summary for next session
echo ""
echo "💾 Saving session summary..."
cat > .claude/last-session-summary.txt <<EOF
Last Session: $(date)
Summary: $SESSION_SUMMARY
Deployed: ${DEPLOYED:-No}
Uncommitted Changes: $UNCOMMITTED
Unpushed Commits: $UNPUSHED
EOF

echo "   ✅ Saved to .claude/last-session-summary.txt"

# 6. Remind about documentation updates
echo ""
echo "📚 Documentation Update Checklist:"
echo "   [ ] docs/DEPLOYMENT_STATUS.md - if deployed"
echo "   [ ] docs/PROJECT_PHASE.md - handoff notes"
echo "   [ ] Update 'Last Updated' timestamps"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "✅ Session context captured. See you next time!"
echo "═══════════════════════════════════════════════════════════"
