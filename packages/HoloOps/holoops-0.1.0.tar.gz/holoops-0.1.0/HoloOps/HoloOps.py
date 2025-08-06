from pathlib import Path
from typing import Mapping, Any, Optional, Callable
import threading
import shutil
import os
import sys
import tempfile

from .HOUtils.HOUtils import *

# def detectProject():
#     mainMod = sys.modules.get("__main__")
#     if mainMod and hasattr(mainMod, "__file__"):
#         entryPath = Path(mainMod.__file__).resolve()
#         projectName = entryPath.stem
#         for ancestor in entryPath.parents:
#             if ancestor.name == projectName:
#                 return ancestor.parent, projectName
#     cwd = Path.cwd().resolve()
#     return cwd, cwd.name

# def createMarkerFile(projectRoot: Path, markerFile: str) -> Path:
#     markerPath = projectRoot / markerFile
#     if not markerPath.exists():
#         markerPath.touch()
#     return markerPath

class HoloOps:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        projectName: Optional[str] = None,
        baseDirs: Optional[Mapping[str, Path]] = None,
        mappingConfig: Optional[Mapping[str, Mapping[str, list[str]]]] = None,
        markerFile: Optional[str] = None,
        storageOptionFn: Optional[Callable[[], str]] = None,
        cloudProviders: Optional[list[str]] = None,
        excludedDirs: Optional[list[str]] = None,
        useDotenv: bool = False,
        dotenvOverride: bool = True
    ):
        # Already initialized? Don't re-run setup.
        if getattr(self, "_initialized", False):
            return

        # --- Configurable properties, defaults to None ---
        self.projectName = projectName
        self.markerFile = markerFile
        self.cloudProviders = cloudProviders or [
            "OneDrive", "Google Drive", "Google Drive File Stream", "Dropbox", "iCloudDrive", "Box", "pCloudDrive"
        ]
        self.excludedDirs = excludedDirs or ['.vs', 'bin', 'obj', '__pycache__', '.git']
        self.baseDirs = baseDirs
        self.mappingConfig = mappingConfig
        self.storageOptionFn = storageOptionFn or (lambda: os.getenv("STORAGE_OPTION", "local").lower())
        self.useDotenv = useDotenv
        self.dotenvOverride = dotenvOverride

        # Only run full setup if projectName is set!
        if self.projectName is not None:
            self._internalSetup()
        self._initialized = True

    def _internalSetup(self):
        # Any side effects/configuration that must happen after properties are set.
        if self.useDotenv:
            try:
                from dotenv import load_dotenv
                load_dotenv(override=self.dotenvOverride)
            except ImportError:
                pass

        self.markerFile = self.markerFile or f".{self.projectName}"
        self.baseDirs = self.baseDirs or self._defaultBaseDirs()
        self.mappingConfig = self.mappingConfig or {}

        self._assignComponentDirs()
        self._ensureAllDirs()
        self._migrateLocalToCloud()

    def _defaultBaseDirs(self) -> dict:
        root = Path.cwd().resolve()
        name = self.projectName or "default"
        return {
            "default": root / name
        }

    def _findCloudDir(self) -> Optional[Path]:
        home = Path.home()
        for folder in home.iterdir():
            if folder.is_dir() and any(cloud.lower() in folder.name.lower() for cloud in self.cloudProviders):
                return folder
        return None

    def _assignComponentDirs(self):
        def assignFromMap(baseDir: Path, mapping: dict):
            for name, parts in mapping.items():
                setattr(self, name, baseDir.joinpath(*parts))
        for key, mapping in (self.mappingConfig or {}).items():
            baseDir = self.baseDirs.get(key)
            if baseDir is not None:
                assignFromMap(baseDir, mapping)

    def _ensureAllDirs(self):
        for attr in dir(self):
            val = getattr(self, attr)
            if isinstance(val, Path):
                val.mkdir(parents=True, exist_ok=True)
            elif isinstance(val, dict):
                for v in val.values():
                    if isinstance(v, Path):
                        v.mkdir(parents=True, exist_ok=True)

    def _migrateLocalToCloud(self):
        if self.storageOptionFn() != "cloud":
            return
        if "local" not in self.baseDirs or "cloud" not in self.baseDirs:
            return
        src = self.baseDirs["local"]
        dst = self.baseDirs["cloud"]
        if src.exists():
            self._copyDir(src, dst)

    def _copyDir(self, source: Path, target: Path) -> int:
        target.mkdir(parents=True, exist_ok=True)
        count = 0
        for item in source.rglob("*"):
            dest = target / item.relative_to(source)
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            elif not dest.exists():
                shutil.copy2(item, dest)
                count += 1
        return count

    def getDir(self, name: str) -> Optional[Path]:
        return getattr(self, name, None)

    def setProperty(self, name: str, value: Any):
        """
        Set a property and, if it's a major config (like baseDirs or mappingConfig),
        re-run internal setup so changes take effect immediately. Supports
        passing a dict of properties for batch setting.
        """
        if isinstance(name, dict):
            for k, v in name.items():
                self.setProperty(k, v)
            return self
        setattr(self, name, value)
        # Only run full setup if projectName is now set
        if self.projectName is not None and name in (
            "baseDirs", "mappingConfig", "projectName", "markerFile"
        ):
            self._internalSetup()
        return self  # allows chaining

    setAttr = setProperty  # Alias

    def excludeDirs(self) -> list[str]:
        return self.excludedDirs

    # --- Project Management ---

    @staticmethod
    def findProject():
        return detectProject()

    @staticmethod
    def detectProject():
        return detectProject()

    @staticmethod
    def createMarker(projectRoot: Path, markerFile: str = ".project_marker") -> Path:
        return createMarkerFile(projectRoot, markerFile)

    @staticmethod
    def createMarkerFile(projectRoot: Path, markerFile: str = ".project_marker") -> Path:
        return createMarkerFile(projectRoot, markerFile)

    # --- Directory Management ---

    @staticmethod
    def makeDir(path: Path | str, exist_ok=True) -> Path:
        return makeDir(path, exist_ok=exist_ok)

    @staticmethod
    def removeDir(path: Path | str):
        return removeDir(path)

    @staticmethod
    def moveDir(src: Path | str, dst: Path | str):
        return moveDir(src, dst)

    @staticmethod
    def listDirs(path: Path | str) -> list[Path]:
        return listDirs(path)

    @staticmethod
    def dirExists(path: Path | str) -> bool:
        return dirExists(path)

    # --- File Management ---

    @staticmethod
    def safeWriteFile(path: Path | str, data: bytes | str, mode: str = "w"):
        return safeWriteFile(path, data, mode)

    @staticmethod
    def makeTempFile(suffix="", prefix="tmp", dir=None, delete=False):
        return makeTempFile(suffix=suffix, prefix=prefix, dir=dir, delete=delete)

    @staticmethod
    def writeFile(path: Path | str, data: bytes | str, mode: str = "w"):
        return writeFile(path, data, mode)
    @staticmethod
    def appendFile(path: Path | str, data: bytes | str, mode: str = "a"):
        return appendFile(path, data, mode)

    @staticmethod
    def readFile(path: Path | str, mode: str = "r") -> str | bytes:
        return readFile(path, mode)

    @staticmethod
    def touchFile(path: Path | str):
        return touchFile(path)

    @staticmethod
    def copyFile(src: Path | str, dst: Path | str):
        return copyFile(src, dst)

    @staticmethod
    def moveFile(src: Path | str, dst: Path | str):
        return moveFile(src, dst)

    @staticmethod
    def removeFile(path: Path | str):
        return removeFile(path)

    @staticmethod
    def listFiles(path: Path | str, pattern: str = "*", mode: str = "nRecursive") -> list[Path]:
        return listFiles(path, pattern, mode)

    @staticmethod
    def fileExists(path: Path | str) -> bool:
        return Path(path).is_file()

    @staticmethod
    def setPermissions(path: Path | str, mode: int):
        return setPermissions(path, mode)

    @staticmethod
    def makeSymlink(target: Path | str, link: Path | str):
        return makeSymlink(target, link)

    @staticmethod
    def isSymlink(path: Path | str) -> bool:
        return isSymlink(path)

    @staticmethod
    def resolveSymlink(path: Path | str) -> Path:
        return resolveSymlink(path)

    @staticmethod
    def getFileInfo(path: Path | str) -> dict:
        return getFileInfo(path)
