import gzip, io, tarfile
from IPython.display import FileLink, display

ARCHIVE = WORKDIR / 'submission_competitive_v46.tar.gz'
EXPECTED_ARCHIVE_SHA256 = '7cfb4ab837e7d809a89ba4876a8508533e115c51556e82c97888069138659a6b'
with ARCHIVE.open('wb') as file:
    with gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.GNU_FORMAT) as tar:
            info = tarfile.TarInfo('main.py')
            info.size, info.mode, info.mtime = len(source_bytes), 0o644, 0
            tar.addfile(info, io.BytesIO(source_bytes))
with tarfile.open(ARCHIVE) as tar:
    assert tar.getnames() == ['main.py']
    assert tar.extractfile('main.py').read() == source_bytes
assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == EXPECTED_ARCHIVE_SHA256
build_manifest = {'version': 'v46', 'classification': 'evaluated_upgrade', 'protocol': 'EXP293 first-turn microstructure, two-turn sale advance, sales-first market order, lost-race detector and imminence-ordered reservation on the frozen EXP288 policy', 'independent_reacting_confirmation_passed': True, 'complete_physical_audit_passed': True, 'isolated_runtime_passed': False, 'isolated_runtime_max_ms': 85.08, 'local_50ms_rule': 'waived by the user for the step-712 closure planner (WAIVER293.json); engine actTimeout 1 s', 'linux_replay_passed': True, 'live_recorded_rival_replay_games': None, 'main_sha256': '735c370383b70d3bf3aac792f2c147e0afc99166fc9f253ede10e8a030acedb6', 'archive_sha256': '7cfb4ab837e7d809a89ba4876a8508533e115c51556e82c97888069138659a6b', 'source_integrity': 'PASS', 'archive_integrity': 'PASS', 'optional_game_checks': 'NOT RUN', 'live_rating_guarantee': None}
(WORKDIR / 'v46_manifest.json').write_text(json.dumps(build_manifest, indent=2))
print('PACKAGE READY:', ARCHIVE.name, '|', ARCHIVE.stat().st_size, 'bytes', flush=True)
print('SHA-256:', EXPECTED_ARCHIVE_SHA256, flush=True)
display(FileLink(ARCHIVE.name))
