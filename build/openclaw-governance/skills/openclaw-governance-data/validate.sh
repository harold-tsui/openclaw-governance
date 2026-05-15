#!/bin/bash
set -e
PATH_ARG=""
CLASS_ARG=""
REFS_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      PATH_ARG="$2"
      shift 2
      ;;
    --class)
      CLASS_ARG="$2"
      shift 2
      ;;
    --refs)
      REFS_ARG="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done
STATUS="OK"
VIOLATIONS=()
SUGGEST=""
if [[ -z "$PATH_ARG" ]]; then
  STATUS="ERROR"
  VIOLATIONS+=("E_FIELD_MISSING:deliverable_path")
fi
if [[ -z "$REFS_ARG" ]]; then
  STATUS="ERROR"
  VIOLATIONS+=("E_FIELD_MISSING:context_refs")
fi
if [[ -n "$PATH_ARG" ]] && [[ "$PATH_ARG" != *"/deliverables/"* ]]; then
  STATUS="ERROR"
  VIOLATIONS+=("E_PATH_FORBIDDEN:$PATH_ARG")
  BASE_DIR="$(dirname "$PATH_ARG")"
  SUGGEST="${BASE_DIR}/deliverables/$(basename "$PATH_ARG")"
fi
if [[ -n "$CLASS_ARG" ]] && [[ -n "$PATH_ARG" ]] && [[ "$PATH_ARG" == *"/deliverables/"* ]]; then
  case "$CLASS_ARG" in
    P0|P1|P2|P3) ;;
    *)
      STATUS="ERROR"
      VIOLATIONS+=("E_CLASS_MISMATCH:$CLASS_ARG")
      ;;
  esac
fi
printf '{'
printf '"status":"%s",' "$STATUS"
printf '"violations":['
FIRST=1
for v in "${VIOLATIONS[@]}"; do
  if [[ $FIRST -eq 1 ]]; then FIRST=0; else printf ','; fi
  IFS=':' read -r code detail <<< "$v"
  printf '{"id":"%s","desc":"%s"}' "$code" "$detail"
done
printf ']'
if [[ -n "$SUGGEST" ]]; then
  printf ',"suggest_path":"%s"' "$SUGGEST"
fi
printf '}\n'
