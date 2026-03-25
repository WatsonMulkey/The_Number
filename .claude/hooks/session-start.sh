#!/bin/bash
# Session Start Context Loader
# Multi-project workspace - detects and loads relevant context

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo -e "${BLUE}  Dev Workspace - Session Start${NC}"
echo -e "${BLUE}══════════════════════════════════════════${NC}"
echo ""

# Main repo git status
echo -e "${GREEN}Git Status:${NC}"
LATEST=$(git log -1 --oneline 2>/dev/null || echo "N/A")
echo "  Latest: $LATEST"
MODIFIED=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
if [ "$MODIFIED" != "0" ]; then
    echo -e "  ${YELLOW}${MODIFIED} uncommitted changes${NC}"
fi
echo ""

# Project health dashboard
# Checks all directories with CLAUDE.md, plus known separate repos
echo -e "${GREEN}Projects:${NC}"

check_project() {
    local dir="$1"
    local name=""
    local project_status=""
    local git_info=""

    # Get project name from CLAUDE.md header
    if [ -f "${dir}/CLAUDE.md" ]; then
        name=$(head -1 "${dir}/CLAUDE.md" 2>/dev/null | sed 's/^# //')
    fi
    name="${name:-no CLAUDE.md}"

    # Get project lifecycle status from CLAUDE.md (## Status: line)
    if [ -f "${dir}/CLAUDE.md" ]; then
        local raw_status=$(grep -m1 '^## Status:' "${dir}/CLAUDE.md" 2>/dev/null | sed 's/^## Status: //')
        if [ -n "$raw_status" ]; then
            # Color based on first word
            local first_word=$(echo "$raw_status" | awk '{print $1}')
            case "$first_word" in
                Active|Active*)  project_status="${GREEN}${raw_status}${NC}" ;;
                Paused|Paused*)  project_status="${DIM}${raw_status}${NC}" ;;
                Complete|Complete*) project_status="${DIM}${raw_status}${NC}" ;;
                Blocked|Blocked*) project_status="${RED}${raw_status}${NC}" ;;
                *)               project_status="${raw_status}" ;;
            esac
        fi
    fi

    # Check if this directory has its own git repo
    if [ -d "${dir}/.git" ]; then
        local dirty=$(cd "$dir" && git status --short 2>/dev/null | wc -l | tr -d ' ')
        local unpushed=$(cd "$dir" && git log --oneline '@{upstream}..HEAD' 2>/dev/null | wc -l | tr -d ' ')
        local branch=$(cd "$dir" && git branch --show-current 2>/dev/null)

        if [ "$dirty" != "0" ] && [ "$unpushed" != "0" ]; then
            git_info=" ${DIM}(${branch})${NC} [${YELLOW}${dirty} uncommitted, ${unpushed} unpushed${NC}]"
        elif [ "$dirty" != "0" ]; then
            git_info=" ${DIM}(${branch})${NC} [${YELLOW}${dirty} uncommitted${NC}]"
        elif [ "$unpushed" != "0" ]; then
            git_info=" ${DIM}(${branch})${NC} [${YELLOW}${unpushed} unpushed${NC}]"
        else
            git_info=" ${DIM}(${branch}) clean${NC}"
        fi
    fi

    # Output: name + git info on first line, status on second (indented)
    echo -e "  ${dir}/ - ${name}${git_info}"
    if [ -n "$project_status" ]; then
        echo -e "    ${project_status}"
    fi
}

# Scan for all project directories (CLAUDE.md or known projects)
for dir in foil-industries-v2 frontend resume-tailor rag-vault audio-scribe mp3-to-midi mixdiff buyer-mode sample-vault; do
    if [ -d "$dir" ]; then
        check_project "$dir"
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
