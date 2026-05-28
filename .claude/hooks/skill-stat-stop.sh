#!/usr/bin/env bash
# Stop 훅: 턴이 끝날 때 해당 세션에 열려 있던 스킬을 마감한다.
# elapsed = (턴 종료 시각) - (스킬 호출 시각). 마감 후 pending 파일 삭제.
# 훅은 절대 세션을 막으면 안 되므로 항상 exit 0 으로 끝낸다.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
STATS_DIR="$PROJECT_DIR/.claude/stats"
PENDING_DIR="$STATS_DIR/pending"
LOG="$STATS_DIR/skill-usage.jsonl"
mkdir -p "$PENDING_DIR" 2>/dev/null

input=$(cat)
now_ms=$(jq -n 'now * 1000 | floor')
session=$(printf '%s' "$input" | jq -r '.session_id // "unknown"')

safe_session=$(printf '%s' "$session" | tr -c 'A-Za-z0-9._-' '_')
pending="$PENDING_DIR/$safe_session.json"

if [ -f "$pending" ]; then
  skill=$(jq -r '.skill // "unknown"' "$pending")
  start=$(jq -r '.start_ms // 0' "$pending")
  elapsed=$(( now_ms - start ))
  jq -nc --argjson ts "$now_ms" --arg session "$session" --arg skill "$skill" --argjson elapsed_ms "$elapsed" \
    '{ts:$ts, session:$session, skill:$skill, elapsed_ms:$elapsed_ms}' >> "$LOG"
  rm -f "$pending"
fi

exit 0
