#!/usr/bin/env bash
# Task 75: restart arena-service as a SURVIVABLE daemon.
# Lesson: processes started in a tool-session shell get killed when that call
# ends (even with nohup/setsid single-fork). A python double-fork daemon
# escapes the session and survives across tool calls / agent sessions.
# Also: `bun --hot` does NOT reload files replaced via git rename — after any
# `git checkout/reset` touching index.ts, run this script.
python3 - << 'PYEOF'
import os
log = open('/tmp/arena-service.log', 'ab', buffering=0)
pid = os.fork()
if pid == 0:
    os.setsid()
    if os.fork() == 0:
        os.chdir('/home/z/my-project/mini-services/arena-service')
        os.dup2(log.fileno(), 1); os.dup2(log.fileno(), 2)
        os.execvp('bun', ['bun', '--hot', 'index.ts'])
        os._exit(1)
    os._exit(0)
os.waitpid(pid, 0)
print('arena-service daemon forked (see /tmp/arena-service.log)')
PYEOF
