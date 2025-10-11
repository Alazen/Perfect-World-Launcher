import os
import sys
from pathlib import Path


def _copy_resource(source: Path, target: Path) -> None:
    if not source.exists() or target.exists():
        return
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    except Exception:
        temp_target = target.with_suffix(target.suffix + '.tmp')
        try:
            temp_target.write_bytes(source.read_bytes())
            temp_target.replace(target)
        except Exception:
            temp_target.unlink(missing_ok=True)


SETTINGS_DIR_NAME = 'PerfectWorldLauncher'

def _dir_is_writable(directory: Path) -> bool:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / '.__pwlauncher_probe'
        probe.write_text('ok', encoding='utf-8')
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def _iter_settings_targets(base_dir: Path) -> list[Path]:
    targets: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path) -> None:
        key = str(path.resolve() if path.exists() else path)
        if key in seen:
            return
        seen.add(key)
        targets.append(path)

    if _dir_is_writable(base_dir):
        _add(base_dir / 'settings.json')
    appdata = os.getenv('APPDATA')
    if appdata:
        _add(Path(appdata) / SETTINGS_DIR_NAME / 'settings.json')
    else:
        _add(Path.home() / SETTINGS_DIR_NAME / 'settings.json')
    return targets


def _copy_default_resources() -> None:
    if not getattr(sys, 'frozen', False):
        return
    source_root = Path(getattr(sys, '_MEIPASS', ''))
    if not source_root:
        return
    base_dir = Path(sys.executable).resolve().parent
    settings_source = source_root / 'launcher' / 'ui' / 'settings.json'
    for target in _iter_settings_targets(base_dir):
        _copy_resource(settings_source, target)


_copy_default_resources()

