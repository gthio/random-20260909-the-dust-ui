#!/usr/bin/env bash
# Catch stack-specific leaks in the chassis.
#
# Stack-specific knowledge (Python idioms, paths, manifest names) belongs in
# the external knowledge repo, not the chassis. Anything in .agents/prompts/
# or .agents/context.md must use ${PLACEHOLDERS}.
#
# Lines containing the literal string `chassis-allow` are exempt — use this
# only for documented, intentional examples that reference a specific stack
# (e.g. an in-comment hint pointing at a stack convention).
#
# Templates under .agents/templates/ are not scanned: they are scaffolds that
# legitimately contain example fills.
#
# Usage:
#   bash .agents/check-chassis.sh
#
# Exit 0 if clean, 1 if leaks are found.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

CHASSIS_PATHS=(
  ".agents/prompts"
  ".agents/context.md"
  ".claude/commands"
)

# Each entry: REGEX|HUMAN-READABLE LABEL
PATTERNS=(
  '\bsrc/|bare src/ path — use ${SRC_PATH}'
  '\btests/|bare tests/ path — use ${TESTS_DIR}'
  'pyproject\.toml|literal pyproject.toml — use ${BUILD_MANIFEST}'
  'os\.getenv|literal os.getenv (Python-specific) — reference the stack convention'
  '\buv run\b|bare "uv run" — use ${CLI_SCRIPT} (full prefix already includes it)'
)

violations=0
for entry in "${PATTERNS[@]}"; do
  pattern="${entry%%|*}"
  label="${entry#*|}"
  matches=$(grep -rEn "$pattern" "${CHASSIS_PATHS[@]}" 2>/dev/null | grep -v 'chassis-allow' || true)
  if [[ -n "$matches" ]]; then
    echo "==> Leak: $label"
    echo "$matches" | sed 's/^/    /'
    echo
    violations=$((violations + 1))
  fi
done

if (( violations > 0 )); then
  echo "Found $violations leak pattern(s) in the chassis."
  echo "Either move the content to the knowledge repo, replace the literal"
  echo "with a \${PLACEHOLDER}, or append 'chassis-allow' to the line if it's a"
  echo "documented example that intentionally references a specific stack."
  exit 1
fi

echo "Chassis clean: no stack-specific leaks in"
for path in "${CHASSIS_PATHS[@]}"; do echo "  - $path"; done
