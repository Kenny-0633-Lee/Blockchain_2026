"""
_common/demo_kit.py — 특강 시연 공통 도구 (터미널 연출)

모든 시연 스크립트가 같은 조작법을 갖도록 한 곳에 모았습니다.

  Enter  : 다음 단계로          q + Enter : 종료
  a      : 남은 단계를 멈춤 없이 끝까지 (a + Enter)

실행 옵션 (모든 시연 공통)
  --auto   멈춤 없이 진행 (애니메이션은 유지)
  --fast   애니메이션 지연 없음 (리허설/점검용)
  --web    브라우저 시각화 열기 (해당 시연에 HTML 이 있을 때)
  출력을 파일/파이프로 돌리면 자동으로 --auto --fast 와 같게 동작합니다.

macOS 터미널 / Windows PowerShell·Git Bash 공통. 표준 라이브러리만 사용합니다.
"""
import os
import sys
import time
import webbrowser
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

if os.name == "nt":
    os.system("")  # Windows 콘솔에서 ANSI 색상 활성화

_TTY = sys.stdout.isatty() and sys.stdin.isatty()
PAUSE = _TTY and "--auto" not in sys.argv
ANIM = sys.stdout.isatty() and "--fast" not in sys.argv
COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
_rest_auto = False

_C = {"dim": "2", "red": "31", "green": "32", "yellow": "33", "blue": "34",
      "magenta": "35", "cyan": "36", "bold": "1", "inv": "7"}


def c(text, *styles):
    if not COLOR or not styles:
        return str(text)
    codes = ";".join(_C[s] for s in styles if s in _C)
    if not codes:
        return str(text)
    return f"\033[{codes}m{text}\033[0m"


def sleep(sec):
    if ANIM:
        time.sleep(sec)


def title(text):
    """시연 맨 위 제목"""
    bar = "═" * 70
    print("\n" + c(bar, "cyan"))
    print(c(f"  {text}", "bold", "cyan"))
    print(c(bar, "cyan"))


def step(text, hint="Enter ▶ 다음 단계"):
    """단계 제목을 출력하고 Enter 를 기다린다"""
    pause(hint, before=f"\n{c('■', 'yellow')} {c(text, 'bold')}")


def say(text):
    """말할 포인트 / 설명 한 줄"""
    print(c(f"  ▸ {text}", "dim"))


def line(text="", delay=0.0):
    print(text)
    sys.stdout.flush()
    sleep(delay)


def good(text):
    print(f"  {c('✔', 'green')} {c(text, 'green')}")


def bad(text):
    print(f"  {c('✘', 'red')} {c(text, 'red')}")


def kv(label, value, width=14, color=None):
    v = c(value, color) if color else value
    print(f"  {c(label.ljust(width), 'dim')} {v}")


def pause(hint="Enter ▶ 다음 단계", before=None):
    """before 를 출력하고, 대화형이면 Enter 입력을 기다린다"""
    global _rest_auto
    if before:
        print(before)
    if not PAUSE or _rest_auto:
        return
    try:
        s = input(c(f"  [{hint}] ", "dim")).strip().lower()
    except EOFError:
        _rest_auto = True
        return
    if s == "q":
        print("종료합니다.")
        sys.exit(0)
    if s == "a":
        _rest_auto = True


def live(text):
    """같은 줄을 덮어쓰며 진행 상황 표시 (애니메이션이 꺼져 있으면 무시)"""
    if ANIM:
        sys.stdout.write("\r\033[K" + text if COLOR else "\r" + text)
        sys.stdout.flush()


def live_end(text):
    """진행 표시를 마치고 최종 줄을 확정"""
    if ANIM:
        sys.stdout.write("\r\033[K" if COLOR else "\r")
    print(text)


def bar(frac, width=30, fill="█", empty="░"):
    n = int(round(max(0.0, min(1.0, frac)) * width))
    return fill * n + empty * (width - n)


def hl_prefix(hexstr, zeros):
    """해시에서 앞자리 0 부분을 색칠"""
    z = 0
    while z < len(hexstr) and hexstr[z] == "0" and z < zeros:
        z += 1
    return c(hexstr[:z], "green", "bold") + hexstr[z:]


def open_web(html_path):
    """HTML 시각화를 기본 브라우저로 연다 (macOS/Windows/Linux 공통)"""
    p = Path(html_path).resolve()
    if not p.exists():
        print(f"HTML 파일이 없습니다: {p}")
        return
    print(f"브라우저에서 엽니다: {p}")
    print("  (안 열리면 위 파일을 직접 더블클릭하세요)")
    webbrowser.open(p.as_uri())


def wants_web():
    return "--web" in sys.argv


def done(msg):
    print("\n" + c("─" * 70, "dim"))
    print(c(msg, "bold"))
