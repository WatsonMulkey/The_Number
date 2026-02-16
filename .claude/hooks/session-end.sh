#!/bin/bash
# Session End Hook - Non-interactive context capture
# Called by the Stop hook prompt in settings.local.json
# This script just captures git state; the AI prompt handles the summary

set -e

echo "Capturing session state..."

# Git state
UNCOMMITTED=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
UNPUSHED=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
LATEST=$(git log -1 --oneline 2>/dev/null || echo "N/A")

echo "  Latest commit: $LATEST"
if [ "$UNCOMMITTED" != "0" ]; then
    echo "  Uncommitted changes: $UNCOMMITTED"
fi
if [ "$UNPUSHED" != "0" ]; then
    echo "  Unpushed commits: $UNPUSHED"
fi

echo "Done."
