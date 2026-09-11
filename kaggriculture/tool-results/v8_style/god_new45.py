import sys, glob, gc
sys.path.insert(0, '.')
from god_arena import run_god_arena
for path in sorted(glob.glob('/home/z/my-project/tool-results/v8_style/new45/*.jsonl')):
    tag = path.split('/')[-1].replace('.jsonl', '')
    run_god_arena(path, f'/tmp/god45_{tag}.json')
    gc.collect()
print('done')
