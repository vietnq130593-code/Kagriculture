import ast, gzip, hashlib, io, json, tarfile
from pathlib import Path
try:
    from IPython.display import FileLink, display
except ImportError:
    FileLink = display = None

main_path = WORKDIR / "main.py"
archive_path = WORKDIR / "submission.tar.gz"

packed_hashes = {}
archive_data = io.BytesIO()

with tarfile.open(fileobj=archive_data, mode="w") as archive:
    data = main_path.read_bytes().replace(b'\r\n', b'\n')
    h = hashlib.sha256(data).hexdigest()
    packed_hashes["main.py"] = h
    member = tarfile.TarInfo("main.py")
    member.size, member.mode, member.mtime = len(data), 0o644, 0
    archive.addfile(member, io.BytesIO(data))

submission = gzip.compress(archive_data.getvalue(), mtime=0)
archive_path.write_bytes(submission)

with tarfile.open(fileobj=io.BytesIO(submission), mode="r:gz") as tar:
    names = tar.getnames()
    assert "main.py" in names, "Archive missing main.py!"
    tar_code = tar.extractfile("main.py").read().decode("utf-8")
    ast.parse(tar_code)

arc_sha = hashlib.sha256(submission).hexdigest()
print("VALIDATION PASS: submission.tar.gz", len(submission), "bytes")
print("Archive SHA-256:", arc_sha)
if display and FileLink:
    display(FileLink("submission.tar.gz"))
