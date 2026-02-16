#!/usr/bin/env bash
# validate_env.sh — Checks that all prerequisites for issue-to-beads are met.
# Exit codes: 0 = all good, 1 = missing prerequisites
# Output: JSON with status of each check

set -euo pipefail

errors=()
warnings=()

# Check bd CLI
if command -v bd &>/dev/null; then
  bd_version=$(bd --version 2>/dev/null || echo "unknown")
  bd_status="ok"
else
  bd_status="missing"
  errors+=("bd CLI not found. Install from https://github.com/steveyegge/beads")
fi

# Check gh CLI
if command -v gh &>/dev/null; then
  gh_status="ok"
  # Check gh auth
  if gh auth status &>/dev/null 2>&1; then
    gh_auth="ok"
  else
    gh_auth="not_authenticated"
    errors+=("gh CLI not authenticated. Run 'gh auth login'")
  fi
else
  gh_status="missing"
  gh_auth="n/a"
  errors+=("gh CLI not found. Install from https://cli.github.com")
fi

# Check for .beads directory
if [ -d ".beads" ]; then
  beads_init="ok"
elif [ -d "$(git rev-parse --show-toplevel 2>/dev/null)/.beads" ] 2>/dev/null; then
  beads_init="ok"
else
  beads_init="not_initialized"
  errors+=("Beads not initialized in this project. Run 'bd init'")
fi

# Check for git repo
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  git_repo="ok"
  git_remote=$(git remote get-url origin 2>/dev/null || echo "none")
else
  git_repo="not_a_repo"
  git_remote="n/a"
  errors+=("Not inside a git repository")
fi

# Output JSON
error_count=${#errors[@]}
cat <<EOF
{
  "bd_cli": "$bd_status",
  "gh_cli": "$gh_status",
  "gh_auth": "$gh_auth",
  "beads_initialized": "$beads_init",
  "git_repo": "$git_repo",
  "git_remote": "$git_remote",
  "errors": [$(printf '"%s",' "${errors[@]}" 2>/dev/null | sed 's/,$//')],
  "ready": $([ "$error_count" -eq 0 ] && echo "true" || echo "false")
}
EOF

exit $error_count
