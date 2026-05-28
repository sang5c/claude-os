#!/usr/bin/env python3
"""스킬 사용 통계 표 출력.

데이터 소스: <project>/.claude/stats/skill-usage.jsonl
각 줄: {"ts": <ms>, "session": "...", "skill": "...", "elapsed_ms": <int>}

스킬별로 호출 횟수 / 총 소요 / 평균 소요 / 마지막 사용을 집계해 표로 출력한다.
"""
import json
import os
import sys
import unicodedata
from datetime import datetime


def find_log():
    # 우선순위: 인자 > CLAUDE_PROJECT_DIR > 스크립트 위치 기준 프로젝트 루트
    if len(sys.argv) > 1:
        return sys.argv[1]
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project:
        # .claude/skills/skill-stat/stat.py -> 프로젝트 루트는 3단계 위
        project = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
    return os.path.join(project, ".claude", "stats", "skill-usage.jsonl")


def aggregate(log_path):
    stats = {}
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            skill = rec.get("skill", "unknown")
            elapsed = rec.get("elapsed_ms", 0) or 0
            ts = rec.get("ts", 0) or 0
            s = stats.setdefault(skill, {"count": 0, "total": 0, "last": 0})
            s["count"] += 1
            s["total"] += elapsed
            if ts > s["last"]:
                s["last"] = ts
    return stats


def fmt_dur(ms):
    ms = int(ms)
    if ms < 1000:
        return "{}ms".format(ms)
    sec = ms / 1000.0
    if sec < 60:
        return "{:.1f}s".format(sec)
    minutes = int(sec // 60)
    return "{}m{:.0f}s".format(minutes, sec - 60 * minutes)


def fmt_ts(ms):
    if not ms:
        return "-"
    return datetime.fromtimestamp(ms / 1000.0).strftime("%Y-%m-%d %H:%M")


def dwidth(s):
    # 한글 등 전각 문자는 폭 2로 계산해 표 정렬을 맞춘다
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def pad(s, width):
    return s + " " * (width - dwidth(s))


def render(stats):
    rows = []
    for skill, s in stats.items():
        avg = s["total"] / s["count"] if s["count"] else 0
        rows.append([skill, str(s["count"]), fmt_dur(s["total"]),
                     fmt_dur(avg), fmt_ts(s["last"])])
    rows.sort(key=lambda r: int(r[1]), reverse=True)

    headers = ["스킬", "호출", "총 소요", "평균 소요", "마지막 사용"]
    table = [headers] + rows
    widths = [max(dwidth(row[i]) for row in table) for i in range(len(headers))]

    def line(row):
        return "  ".join(pad(row[i], widths[i]) for i in range(len(headers)))

    sep = "  ".join("-" * widths[i] for i in range(len(headers)))
    out = [line(headers), sep]
    out += [line(r) for r in rows]

    total_calls = sum(int(r[1]) for r in rows)
    out.append("")
    out.append("총 {}개 스킬, 누적 호출 {}회".format(len(rows), total_calls))
    return "\n".join(out)


def main():
    log_path = find_log()
    if not os.path.exists(log_path):
        print("아직 기록된 스킬 사용 데이터가 없습니다.")
        print("(데이터 파일: {})".format(log_path))
        return
    stats = aggregate(log_path)
    if not stats:
        print("아직 기록된 스킬 사용 데이터가 없습니다.")
        return
    print(render(stats))


if __name__ == "__main__":
    main()
