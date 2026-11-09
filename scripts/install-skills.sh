#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == -h || ${1:-} == --help ]]; then
  printf 'Usage: %s [skills-directory]\n' "$0"
  printf 'Default: $CODEX_HOME/skills when set, otherwise $HOME/.agents/skills\n'
  exit 0
fi

if [[ $# -gt 1 || ( $# -eq 1 && -z $1 ) ]]; then
  printf 'Usage: %s [skills-directory]\n' "$0" >&2
  exit 2
fi

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
skills_dir=${1:-${CODEX_HOME:-$HOME/.agents}/skills}
skills=(ailsa-nmr reaction-nmr-review)

for skill in "${skills[@]}"; do
  if [[ ! -f "$repo_dir/skills/$skill/SKILL.md" ]]; then
    printf 'Missing bundled skill: %s\n' "$repo_dir/skills/$skill" >&2
    exit 1
  fi
done

if [[ ! -x "$repo_dir/skills/ailsa-nmr/scripts/ailsa" ]]; then
  printf 'Bundled AILSA launcher is missing or cannot be executed.\n' >&2
  exit 1
fi

mkdir -p -- "$skills_dir"
skills_dir=$(cd -- "$skills_dir" && pwd -P)
lock_dir="$skills_dir/.reaction-nmr-review-install.lock"
if ! mkdir -- "$lock_dir" 2>/dev/null; then
  printf 'Cannot acquire installation lock: %s\n' "$lock_dir" >&2
  exit 1
fi

created=()
cleanup() {
  local status=$?
  local target
  if [[ $status -ne 0 && ${#created[@]} -gt 0 ]]; then
    for target in "${created[@]}"; do
      rm -rf -- "$target" || printf 'Could not remove incomplete install: %s\n' "$target" >&2
    done
  fi
  rmdir -- "$lock_dir" || printf 'Could not remove installation lock: %s\n' "$lock_dir" >&2
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

matches_bundle() {
  local source=$1 target=$2 special_files
  [[ -d "$target" && ! -L "$target" ]] || return 1
  if [[ "$source" == */ailsa-nmr && ! -x "$target/scripts/ailsa" ]]; then
    return 1
  fi
  special_files=$(find "$target" ! -type f ! -type d -print) || return 1
  [[ -z "$special_files" ]] && diff -qr -- "$source" "$target" >/dev/null
}

# Check both destinations before making any changes to installed skills.
for skill in "${skills[@]}"; do
  target="$skills_dir/$skill"
  if [[ -e "$target" || -L "$target" ]] && ! matches_bundle "$repo_dir/skills/$skill" "$target"; then
    printf 'Existing skill differs from the bundle: %s\n' "$target" >&2
    printf 'Back up the existing folder outside the skills directory before replacing it, or use a separate skills directory.\n' >&2
    exit 1
  fi
done

for skill in "${skills[@]}"; do
  target="$skills_dir/$skill"
  if [[ ! -e "$target" && ! -L "$target" ]]; then
    mkdir -- "$target"
    created+=("$target")
    cp -Rp -- "$repo_dir/skills/$skill/." "$target/"
  fi
done

for skill in "${skills[@]}"; do
  target="$skills_dir/$skill"
  if ! matches_bundle "$repo_dir/skills/$skill" "$target"; then
    printf 'Verification failed: %s\n' "$target" >&2
    exit 1
  fi
done

printf 'Both bundled skills are ready in %s\n' "$skills_dir"
printf '  - %s\n' "${skills[@]}"
