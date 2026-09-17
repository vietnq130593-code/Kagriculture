USE_CADENCE = True       # True:  V44 + layers 1, 2, 3, 4 (same file as live submission 56280605)
                         # False: V44 + layers 1, 2, 4    (same file as live submission 56277542)
EXTRA_LAYERS = []        # e.g. ['my_layer'] -> build/my_layer.py is appended after layer 4
VERIFY_LIVE_SHA = True   # assert the live sha256 (default layers only; skipped with EXTRA_LAYERS)

import hashlib, os, tarfile

EXPECTED_SHA256 = {
    True: 'fa9e47d81de5020847c1dbc7ca10d058b227be66deea7c019040fb12a1d99f19',   # four-layer build
    False: '016b9a32248f34477cf5f153119d6f361c39d99a50734e435ac2860f65493fe7',  # three-layer build
}

# How each layer sits in the live main.py: (newline, leading newlines, trailing newlines).
# %%writefile writes the cell text with the platform newline and may add or keep a final
# newline, so each written layer is normalized to LF, trimmed of outer blank lines and
# restored from this table.
LAYER_FORMAT = {
    'layer1_preguard': ('\n', 1, 2),
    'layer2_lockstep': ('\r\n', 1, 1),
    'layer3_cadence':  ('\n', 2, 1),
    'layer4_yarnherd': ('\r\n', 1, 1),
}


def layer_bytes(name):
    newline, lead, trail = LAYER_FORMAT[name]
    with open(os.path.join('build', name + '.py'), 'rb') as f:
        text = f.read().decode('utf-8').replace('\r', '').strip('\n')
    return ('\n' * lead + text + '\n' * trail).replace('\n', newline).encode('utf-8')


names = ['layer1_preguard', 'layer2_lockstep'] + (['layer3_cadence'] if USE_CADENCE else [])
names += ['layer4_yarnherd']
with open(os.path.join('build', 'v44_base.py'), 'rb') as f:
    source = f.read()
print(f'  v44_base          {len(source):9,d} bytes')
for name in names:
    part = layer_bytes(name)
    source += part
    print(f'  {name:17s} {len(part):9,d} bytes')
for name in EXTRA_LAYERS:
    with open(os.path.join('build', name + '.py'), 'rb') as f:
        part = b'\n' + f.read()
    source += part
    print(f'  {name:17s} {len(part):9,d} bytes (extra layer)')

sha = hashlib.sha256(source).hexdigest()
live = not EXTRA_LAYERS and sha == EXPECTED_SHA256[USE_CADENCE]
if VERIFY_LIVE_SHA and not EXTRA_LAYERS:
    assert live, (f'main.py does not match the live file (sha256 {sha}). '
                  'If you edited a layer on purpose, set VERIFY_LIVE_SHA = False.')

with open('main.py', 'wb') as f:
    f.write(source)
with tarfile.open('submission.tar.gz', 'w:gz') as tar:
    tar.add('main.py', arcname='main.py')
with tarfile.open('submission.tar.gz') as tar:
    members = tar.getnames()

print()
if USE_CADENCE:
    build = 'four-layer (V44 + layers 1, 2, 3, 4)'
else:
    build = 'three-layer (V44 + layers 1, 2, 4)'
if EXTRA_LAYERS:
    build += ' + extra layers ' + ', '.join(EXTRA_LAYERS)
print('build:', build)
print(f'{os.path.abspath("main.py")}: {len(source):,} bytes')
status = '(matches the live file)' if live else '(custom build, not the live file)'
print(f'  sha256 {sha} {status}')
tar_size = os.path.getsize('submission.tar.gz')
print(f'{os.path.abspath("submission.tar.gz")}: {tar_size:,} bytes, members {members}')

# Load main.py the way kaggle_environments does: exec the file and take the last callable.
with open('main.py', encoding='utf-8') as f:
    raw = f.read()
env = {}
exec(compile(raw, os.path.abspath('main.py'), 'exec'), env)
entry = [v for v in env.values() if callable(v)][-1]
print('entry point (last callable):', entry.__name__)