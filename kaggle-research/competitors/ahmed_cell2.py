from pathlib import Path
import os, sys, time

RUN_GAME_CHECKS = False  # Optional: set True to run four full games in the final cell.
WORKDIR = Path('/kaggle/working') if Path('/kaggle/working').is_dir() else Path.cwd()
WORKDIR.mkdir(parents=True, exist_ok=True)
os.chdir(WORKDIR)
print('V46 started. No training, download or installation is needed.', flush=True)
print('Output directory:', WORKDIR, flush=True)
