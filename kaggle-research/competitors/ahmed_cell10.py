if not RUN_GAME_CHECKS:
    print('Optional game checks skipped. Your verified submission package is already ready.', flush=True)
    print('To play four smoke games, set RUN_GAME_CHECKS = True in cell 1 and run all cells again.', flush=True)
else:
    import contextlib, importlib.metadata
    try:
        engine_version = importlib.metadata.version('kaggle-environments')
    except importlib.metadata.PackageNotFoundError:
        engine_version = None
    if engine_version != '1.32.7':
        print('Optional games require kaggle-environments 1.32.7; installed:', engine_version, flush=True)
        print('No installation was started. The submission archive above remains valid.', flush=True)
    else:
        print('Loading official engine 1.32.7...', flush=True)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
            from kaggle_environments.agent import get_last_callable
        official_entry = get_last_callable(source_bytes.decode('utf-8'), path=str(MAIN))
        assert official_entry is official_entry.__globals__['agent']
        games = []
        for label, opponent in [('self-play', str(MAIN)), ('starter', 'starter')]:
            for seed in (7, 1234):
                print(f'Game {len(games)+1}/4: {label}, seed={seed}', flush=True)
                started = time.perf_counter()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    env = make('kaggriculture', configuration={'episodeSteps':720, 'seed':seed})
                    final = env.run([str(MAIN), opponent])[-1]
                statuses = [row['status'] for row in final]
                rewards = [row['reward'] for row in final]
                assert statuses == ['DONE', 'DONE'], (label, seed, statuses)
                if label == 'starter':
                    assert rewards[0] > rewards[1], (label, seed, rewards)
                games.append({'opponent':label, 'seed':seed, 'rewards':rewards, 'status':statuses})
                print('DONE:', rewards, '|', round(time.perf_counter()-started, 2), 'seconds', flush=True)
        (WORKDIR / 'v46_smoke_results.json').write_text(json.dumps(games, indent=2))
        build_manifest['optional_game_checks'] = 'PASS'
        build_manifest['games'] = games
        (WORKDIR / 'v46_manifest.json').write_text(json.dumps(build_manifest, indent=2))
        print('All four full-game checks passed. The archive has not changed.', flush=True)
