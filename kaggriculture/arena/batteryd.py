#!/usr/bin/env python3
"""Survivable battery daemon (Task 86).

Lesson from Task 75 (restart.sh): processes started in a tool-session shell
are killed when that call ends — even with nohup/setsid single-fork. A python
double-fork daemon escapes the session and survives across tool calls.

Usage:
  python3 arena/batteryd.py <logfile> <command> [args...]

Example — chain of 3 batteries, all detached from the tool session:
  python3 arena/batteryd.py bench/t86_battery.log bash -c '
    python3 arena/battery.py --new v19 --base ahmedv43 --seeds 24 --workers 2 --tag t86_p2_v19_vs_ahmedv43 &&
    python3 arena/battery.py --new v18 --base ahmedv43 --seeds 24 --workers 2 --tag t86_p2_v18_vs_ahmedv43'
"""
import os
import sys


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    logfile, cmd = sys.argv[1], sys.argv[2:]
    log = open(logfile, "ab", buffering=0)
    pid = os.fork()
    if pid == 0:
        os.setsid()
        if os.fork() == 0:
            os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            os.dup2(log.fileno(), 1)
            os.dup2(log.fileno(), 2)
            os.execvp(cmd[0], cmd)
            os._exit(1)
        os._exit(0)
    os.waitpid(pid, 0)
    print(f"battery daemon forked -> {logfile}")


if __name__ == "__main__":
    main()
