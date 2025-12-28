#!/bin/bash
# Session Start Context Loader
# Runs at the beginning of every Claude Code session

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}         The Number - Session Start Context${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Show project phase
if [ -f "docs/PROJECT_PHASE.md" ]; then
    echo -e "${GREEN}📋 Current Phase:${NC}"
    head -5 docs/PROJECT_PHASE.md | grep -v "^#" | grep -v "^$" || echo "  (see docs/PROJECT_PHASE.md)"
    echo ""
fi

# 2. Show deployment status
if [ -f "docs/DEPLOYMENT_STATUS.md" ]; then
    echo -e "${GREEN}🚀 Deployment Status:${NC}"
    cat docs/DEPLOYMENT_STATUS.md | grep -E "(Production|Backend|Local|Known Issues)" | head -10
    echo ""
fi

# 3. Git status
echo -e "${GREEN}📁 Git Status:${NC}"
echo "  Latest commit: $(git log -1 --oneline)"
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$AHEAD" != "0" ]; then
    echo -e "  ${YELLOW}⚠️  $AHEAD commits ahead of origin/main${NC}"
fi
MODIFIED=$(git status --short | wc -l)
if [ "$MODIFIED" != "0" ]; then
    echo -e "  ${YELLOW}⚠️  $MODIFIED uncommitted changes${NC}"
fi
echo ""

# 4. Production health check
echo -e "${GREEN}🌐 Production Status:${NC}"
BACKEND_HEALTH=$(curl -s https://the-number-budget.fly.dev/health 2>&1 | grep -o '"status":"[^"]*"' || echo "❌ Backend unreachable")
echo "  Backend: $BACKEND_HEALTH"
echo "  Frontend: https://foil.engineering/TheNumber (check manually)"
echo ""

# 5. Required reading reminder
echo -e "${YELLOW}📚 REQUIRED READING (if not already reviewed):${NC}"
echo "  1. docs/DEPLOYMENT_STATUS.md - What's actually deployed"
echo "  2. docs/SESSION_START.md - Full checklist"
echo "  3. docs/PROJECT_PHASE.md - Current priorities"
echo ""

#6. Show last session summary if exists
if [ -f ".claude/last-session-summary.txt" ]; then
    echo -e "${GREEN}📝 Last Session Summary:${NC}"
    cat .claude/last-session-summary.txt
    echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Context loaded. Ready to work!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
