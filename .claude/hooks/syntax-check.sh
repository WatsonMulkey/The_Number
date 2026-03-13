#!/bin/bash

# Post-edit syntax check hook
# Runs py_compile on .py files and tsc on .ts files after edits

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Python syntax check
if [[ "$FILE_PATH" == *.py ]]; then
  OUTPUT=$(python -m py_compile "$FILE_PATH" 2>&1)
  if [ $? -ne 0 ]; then
    echo "Python syntax error in $FILE_PATH:" >&2
    echo "$OUTPUT" >&2
    exit 2
  fi
fi

# TypeScript type check
if [[ "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx ]]; then
  OUTPUT=$(npx tsc --noEmit 2>&1)
  if [ $? -ne 0 ]; then
    echo "TypeScript errors:" >&2
    echo "$OUTPUT" >&2
    exit 2
  fi
fi

exit 0
