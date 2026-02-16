#!/bin/bash
# Session Start Context Loader
# Multi-project workspace - detects and loads relevant context

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo -e "${BLUE}  Dev Workspace - Session Start${NC}"
echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo ""

# Git status
echo -e "${GREEN}Git Status:${NC}"
LATEST=$(git log -1 --oneline 2>/dev/null || echo "N/A")
echo "  Latest: $LATEST"
MODIFIED=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
if [ "$MODIFIED" != "0" ]; then
    echo -e "  ${YELLOW}${MODIFIED} uncommitted changes${NC}"
fi
echo ""

# List projects with CLAUDE.md
echo -e "${GREEN}Projects:${NC}"
for dir in foil-industries-v2 frontend resume-tailor rag-vault; do
    if [ -d "$dir" ]; then
        MARKER=""
        if [ -f "${dir}/CLAUDE.md" ]; then
            MARKER=$(head -1 "${dir}/CLAUDE.md" 2>/dev/null | sed 's/^# //')
        fi
        echo "  ${dir}/ - ${MARKER:-no CLAUDE.md}"
    fi
done
echo ""

# Last session summary
if [ -f ".claude/last-session-summary.txt" ]; then
    echo -e "${GREEN}Last session:${NC}"
    cat .claude/last-session-summary.txt
    echo ""
fi

echo -e "${GREEN}Ready to work.${NC}"
