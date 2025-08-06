
from pathlib import Path
import threading
from typing import Mapping, Any, Optional, Callable
import shutil
import os
import sys
import tempfile

def detectProject():
    mainMod = sys.modules.get("__main__")
    if mainMod and hasattr(mainMod, "__file__"):
        entryPath = Path(mainMod.__file__).resolve()
        projectName = entryPath.stem
        for ancestor in entryPath.parents:
            if ancestor.name == projectName:
                return ancestor.parent, projectName
    cwd = Path.cwd().resolve()
    return cwd, cwd.name

def createMarkerFile(projectRoot: Path, markerFile: str) -> Path:
    markerPath = projectRoot / markerFile
    if not markerPath.exists():
        markerPath.touch()
    return markerPath


# --- Directory Management ---
def makeDir(path: Path | str, exist_ok=True) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=exist_ok)
    return p

def removeDir(path: Path | str):
    p = Path(path)
    if p.exists() and p.is_dir():
        shutil.rmtree(p)

def moveDir(src: Path | str, dst: Path | str):
    shutil.move(str(src), str(dst))

def listDirs(path: Path | str) -> list[Path]:
    p = Path(path)
    return [x for x in p.iterdir() if x.is_dir()]

def dirExists(path: Path | str) -> bool:
    return Path(path).is_dir()

# --- File Management ---
def writeFile(path: Path | str, data: bytes | str, mode: str = "w"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    _mode = _normalizeMode(mode, data)
    with open(p, _mode) as f:
        f.write(data)

def appendFile(path: Path | str, data: bytes | str, mode: str = "a"):
    return writeFile(path, data, mode=mode)

def readFile(path: Path | str, mode: str = "r") -> str | bytes:
    _mode = _normalizeMode(mode)
    with open(path, _mode) as f:
        return f.read()

def touchFile(path: Path | str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).touch()

def copyFile(src: Path | str, dst: Path | str):
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dst))

def moveFile(src: Path | str, dst: Path | str):
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))

def removeFile(path: Path | str):
    p = Path(path)
    if p.exists() and p.is_file():
        p.unlink()

def listFiles(path: Path | str, pattern: str = "*", mode: str = "nRecursive") -> list[Path]:
    if mode == "nRecursive":
        return _listFilesNR(path, pattern)
    elif mode == "Recursive":
        return _listFilesR(path, pattern)
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'nRecursive' or 'Recursive'.")

def fileExists(path: Path | str) -> bool:
    return Path(path).is_file()

def setPermissions(path: Path | str, mode: int):
    os.chmod(str(path), mode)

def makeSymlink(target: Path | str, link: Path | str):
    Path(link).parent.mkdir(parents=True, exist_ok=True)
    Path(link).symlink_to(target)

def isSymlink(path: Path | str) -> bool:
    return Path(path).is_symlink()

def resolveSymlink(path: Path | str) -> Path:
    return Path(path).resolve()

def getFileInfo(path: Path | str) -> dict:
    p = Path(path)
    return {
        "size": p.stat().st_size,
        "created": p.stat().st_ctime,
        "modified": p.stat().st_mtime,
        "is_dir": p.is_dir(),
        "is_file": p.is_file(),
        "is_symlink": p.is_symlink()
    }

def safeWriteFile(path: Path | str, data: bytes | str, mode: str = "w"):
    tmpPath = str(path) + ".tmp"
    writeFile(tmpPath, data, mode)
    moveFile(tmpPath, path)

def makeTempFile(suffix="", prefix="tmp", dir=None, delete=False):
    return tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, dir=dir, delete=delete).name

# --- Private Helpers ---
def _normalizeMode(mode: str, data: Any = None) -> str:
    if "b" in mode:
        return mode
    if data is not None and isinstance(data, bytes) and "b" not in mode:
        return mode.replace("t", "") + "b"
    return mode + "t" if "t" not in mode else mode

def _listFilesNR(path: Path | str, pattern: str = "*") -> list[Path]:
    p = Path(path)
    return list(p.glob(pattern))

def _listFilesR(path: Path | str, pattern: str = "*") -> list[Path]:
    p = Path(path)
    return list(p.rglob(pattern))
