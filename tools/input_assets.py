"""Allowlisted, hash-checked candidate input assets; no answer-directory exports."""
import hashlib
from pathlib import Path,PurePosixPath
import shutil
ROOT=Path(__file__).resolve().parents[1]

def checked_asset(asset,root=ROOT):
    name=asset.get("path","")
    relative=PurePosixPath(name)
    if not name or "\\" in name or ":" in name or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Unsafe input asset path")
    if len(relative.parts)<3 or relative.parts[0]!="fixtures" or asset.get("role")!="candidate_input":
        raise ValueError("Only explicitly designated fixtures may be exported")
    base=(root/"fixtures").resolve()
    path=(root/relative).resolve()
    if not path.is_relative_to(base) or not path.is_file(): raise ValueError("Asset escapes fixture root or is missing")
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=asset.get("sha256"): raise ValueError(f"Input asset hash mismatch: {name}")
    return path

def export_assets(assets,output_dir,root=ROOT):
    # Check every source and destination before writing any of them.
    output_dir=Path(output_dir).resolve();pending=[];names=set()
    for asset in assets:
        source=checked_asset(asset,root)
        destination=(output_dir/"assets"/source.name).resolve()
        if not destination.is_relative_to(output_dir) or source.name in names:
            raise ValueError("Unsafe or ambiguous asset destination")
        if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest()!=asset["sha256"]:
            raise ValueError("Refusing to overwrite different input asset")
        names.add(source.name);pending.append((source,destination))
    for source,destination in pending:
        destination.parent.mkdir(parents=True,exist_ok=True)
        if source!=destination: shutil.copyfile(source,destination)
    return [{"path":"assets/"+p.name,"sha256":a["sha256"],"role":"candidate_input"} for a,(p,_) in zip(assets,pending)]
