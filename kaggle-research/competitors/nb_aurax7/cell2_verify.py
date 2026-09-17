import ast, hashlib, importlib.util
from pathlib import Path

main_path = WORKDIR / "main.py"
assert main_path.exists(), "main.py not found!"

code = main_path.read_text(encoding="utf-8")
ast.parse(code)

spec = importlib.util.spec_from_file_location("agent_module", str(main_path))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, "agent") and callable(mod.agent), "agent callable not found!"

main_sha = hashlib.sha256(main_path.read_bytes()).hexdigest()
print(f"main.py SHA-256: {main_sha}")
print("Agent syntax, loading, and callable interface verified successfully.")
