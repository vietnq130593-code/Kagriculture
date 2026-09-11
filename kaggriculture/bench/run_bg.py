"""v6 (Task 27): daemon hóa lệnh battery — double-fork (fork→setsid→fork→exec)
thoát Bash-invocation sweep (PPid=1). Cách dùng:
  SEED_LO=100 SEED_HI=120 BG_LOG=/tmp/bat1.log python bench/run_bg.py \
      python bench/two_sided_v5.py v6.py v5.py bench/v6_vs_v5_100.json
"""
import os
import sys
import time
import subprocess

cmd = sys.argv[1:]
logfile = os.environ.get("BG_LOG", "/tmp/battery_bg.log")
cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pid = os.fork()
if pid == 0:
    os.setsid()
    pid2 = os.fork()
    if pid2 == 0:
        with open(logfile, "ab") as lf:
            lf.write(f"\n=== START {time.ctime()} {' '.join(cmd)}\n".encode())
        with open(logfile, "ab") as out:
            subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, cwd=cwd)
        with open(logfile, "ab") as lf:
            lf.write(f"=== DONE {time.ctime()}\n".encode())
        os._exit(0)
    os._exit(0)
os.waitpid(pid, 0)
print(f"[run_bg] daemon started pid={pid2 if False else 'child'} log={logfile} cwd={cwd}")
