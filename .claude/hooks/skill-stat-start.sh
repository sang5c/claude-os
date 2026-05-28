#!/usr/bin/env bash
# PreToolUse(Skill) 훅: 스킬 호출 시작 시각을 기록한다.
# 같은 턴에서 이미 열린 스킬이 있으면(=직전 스킬) 먼저 마감해 한 턴 내 다중 스킬을 분리 귀속한다.
# 훅은 절대 세션을 막으면 안 되므로 항상 exit 0 으로 끝낸다.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
STATS_DIR="$PROJECT_DIR/.claude/stats"
PENDING_DIR="$STATS_DIR/pending"
LOG="$STATS_DIR/skill-usage.jsonl"
mkdir -p "$PENDING_DIR" 2>/dev/null

input=$(cat)
now_ms=$(jq -n 'now * 1000 | floor')
session=$(printf '%s' "$input" | jq -r '.session_id // "unknown"')
skill=$(printf '%s' "$input" | jq -r '.tool_input.skill // "unknown"')

# 파일명으로 안전한 세션 키
safe_session=$(printf '%s' "$session" | tr -c 'A-Za-z0-9._-' '_')
pending="$PENDING_DIR/$safe_session.json"

# 같은 세션에 열린 스킬이 있으면 마감(다음 스킬 시작 = 이전 스킬 종료)
if [ -f "$pending" ]; then
  prev_skill=$(jq -r '.skill // "unknown"' "$pending")
  prev_start=$(jq -r '.start_ms // 0' "$pending")
  elapsed=$(( now_ms - prev_start ))
  jq -nc --argjson ts "$now_ms" --arg session "$session" --arg skill "$prev_skill" --argjson elapsed_ms "$elapsed" \
    '{ts:$ts, session:$session, skill:$skill, elapsed_ms:$elapsed_ms}' >> "$LOG"
fi

# 새 스킬 진행 기록
jq -nc --arg skill "$skill" --argjson start_ms "$now_ms" \
  '{skill:$skill, start_ms:$start_ms}' > "$pending"

exit 0
