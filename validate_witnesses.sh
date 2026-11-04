#!/usr/bin/env bash
# validate_witnesses.sh
# Usage: ./validate_witnesses.sh <directory> [spec-file.prp]
#
# For every <name>.witness.yml in <directory>, finds <name>.c and runs
# the witness validators on the pair. Logs go to <directory>/results/.

DIR="${1:?Usage: $0 <directory> [spec-file.prp]}"
SPEC="${2:-unreach-call.prp}"
PRP="${SPEC%.prp}"                    # witch wants "unreach-call", not "unreach-call.prp"

RESULTS="$DIR/results"
mkdir -p "$RESULTS"
SUMMARY="$RESULTS/summary.csv"
echo "witness,source,tool,exit_code" > "$SUMMARY"

run_tool() {
  local tool="$1" witness="$2" source="$3"
  local log="$RESULTS/$(basename "${witness%.yml}").$tool.log"

  case "$tool" in
    cpachecker)
      fm-weck expert cpachecker:4.2.2 --witnessValidation \
        --witness "$witness" --spec "$SPEC" --64 "$source" ;;
    cpachecker-violation)
      fm-weck expert cpachecker:4.2.2-validation-violation --witnessValidation \
        --witness "$witness" --spec "$SPEC" --64 "$source" ;;
    witch)
      fm-weck expert witch:svcomp26 --witness-check "$witness" \
        --prp "$PRP" --64 "$source" ;;
    theta)
      # TODO: fill in your Theta validation command here
      echo "theta command not configured" ; return 127 ;;
  esac > "$log" 2>&1

  local rc=$?
  echo "$(basename "$witness"),$(basename "$source"),$tool,$rc" >> "$SUMMARY"
  echo "[$tool] $(basename "$witness") -> exit $rc"
}

TOOLS=(cpachecker cpachecker-violation witch theta)

# Run from inside the directory so relative file names (01.c, unreach-call.prp) resolve
cd "$DIR" || exit 1
RESULTS="results"; SUMMARY="results/summary.csv"

shopt -s nullglob
for witness in *.yml; do
  base="${witness%.witness.yml}"
  [[ "$base" == "$witness" ]] && base="${witness%.yml}"   # fallback if not named *.witness.yml

  source=""
  for ext in c i; do
    [[ -f "$base.$ext" ]] && { source="$base.$ext"; break; }
  done
  if [[ -z "$source" ]]; then
    echo "Skipping $witness: no matching $base.c / $base.i found" >&2
    continue
  fi

  for tool in "${TOOLS[@]}"; do
    run_tool "$tool" "$witness" "$source"
  done
done

echo "Done. Summary: $DIR/results/summary.csv"