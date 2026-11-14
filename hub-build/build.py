#!/usr/bin/env python3
"""
CODEX 게임 관리소 · 임베드 재빌드 스크립트

hub-build/src/*.html 의 게임 원본을 index.html 안의 EMBEDDED(base64) 상수에
그대로 다시 넣습니다. 게임을 고친 뒤에는 아래 한 줄만 실행하면 됩니다.

    python3 hub-build/build.py           # index.html 갱신
    python3 hub-build/build.py --check   # 검증만 (파일 수정 없음)

· codex(RPG)는 별도 배포본(i01041303261.github.io/Codex/)을 그대로 두므로,
  src/codex.html 이 있을 때만 다시 임베드합니다.
· base64 는 UTF-8 원본을 그대로 담습니다(허브의 b64ToUtf8 과 호환).
"""
import base64
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
SRC_DIR = os.path.join(ROOT, "hub-build", "src")

GAMES = ["codex", "math", "history", "mathtower", "elements"]


def load_sources():
    out = {}
    for key in GAMES:
        path = os.path.join(SRC_DIR, key + ".html")
        if os.path.exists(path):
            with open(path, "rb") as f:
                out[key] = f.read()
    return out


def embed(html, key, raw):
    b64 = base64.b64encode(raw).decode("ascii")
    pattern = re.compile(r'(\n  ' + key + r'\s*:\s*")[A-Za-z0-9+/=]*(")')
    if not pattern.search(html):
        raise SystemExit("EMBEDDED 에서 '%s' 키를 찾지 못했습니다." % key)
    return pattern.sub(lambda m: m.group(1) + b64 + m.group(2), html, count=1)


def main():
    check_only = "--check" in sys.argv
    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    sources = load_sources()
    if not sources:
        raise SystemExit("hub-build/src 에 게임 원본이 없습니다.")

    new_html = html
    for key, raw in sources.items():
        new_html = embed(new_html, key, raw)
        print("  embed %-10s %7.1f KB  →  base64 %7.1f KB" % (key, len(raw) / 1024, len(base64.b64encode(raw)) / 1024))

    if check_only:
        same = new_html == html
        print("check:", "최신 상태" if same else "index.html 이 원본과 다릅니다 (재빌드 필요)")
        return 0 if same else 1

    if new_html != html:
        with open(INDEX, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_html)
        print("index.html 갱신 완료 (%d bytes)" % len(new_html.encode("utf-8")))
    else:
        print("변경 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
