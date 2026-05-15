#!/bin/bash
set -e
TYPE_ARG=""
PHASE_ARG=""
DL_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      TYPE_ARG="$2"
      shift 2
      ;;
    --phase)
      PHASE_ARG="$2"
      shift 2
      ;;
    --dl)
      DL_ARG="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done
LEVEL="L2"
RATIONALE=()
STATUS="OK"
if [[ -z "$TYPE_ARG" || -z "$PHASE_ARG" ]]; then
  STATUS="ERROR"
fi
if [[ "$TYPE_ARG" =~ new|first ]]; then
  LEVEL="L3"
  RATIONALE+=("first-time-type")
fi
if [[ "$TYPE_ARG" =~ P0|urgent ]]; then
  LEVEL="L2"
  RATIONALE+=("p0-emergency")
fi
if [[ ${#RATIONALE[@]} -eq 0 ]]; then
  case "$PHASE_ARG" in
    establishing) LEVEL="L3"; RATIONALE+=("phase-default-establishing");;
    transition) LEVEL="L2"; RATIONALE+=("phase-default-transition");;
    cruising) LEVEL="L1"; RATIONALE+=("phase-default-cruising");;
    *) LEVEL="L2"; RATIONALE+=("phase-default-unknown");;
  esac
fi
printf '{'
printf '"level":"%s","status":"%s",' "$LEVEL" "$STATUS"
printf '"rationale":['
FIRST=1
for r in "${RATIONALE[@]}"; do
  if [[ $FIRST -eq 1 ]]; then FIRST=0; else printf ','; fi
  printf '{"rule":"%s","source":"spec"}' "$r"
done
printf ']}\n'
