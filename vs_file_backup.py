# /// script
# requires-python = ">=3.14"
# dependencies = ["platformdirs"]
# ///

import argparse
import logging
import shutil
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

from platformdirs import user_config_dir

APP_NAME = "vs_backup"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
log = logging.getLogger(APP_NAME)
CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_FILE = CONFIG_DIR / "config.toml"

INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}

DEFAULT_BACKUP_FORMAT = "%a_%H%M_%d-%m-%Y"

SAMPLE_CONFIG = """\
backup_destination = "/path/to/backups"
# strftime format for backup filename prefix (default: "%a_%H%M_%d-%m-%Y")
# e.g. "%d-%m-%Y_%H%M" -> 21-02-2026_1602_filename.ext
# backup_format = "%a_%H%M_%d-%m-%Y"

[[files]]
path = "/path/to/important_file.txt"
frequency = "daily"
copies = 7

[[files]]
path = "/path/to/another_file.xlsx"
frequency = "weekly"
copies = 4
"""


def load_config() -> dict:
    """Load config from TOML file, creating a sample if it doesn't exist."""
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(SAMPLE_CONFIG)
        print(f"Created sample config at {CONFIG_FILE}")
        print("Edit it to configure your backups, then run again.")
        raise SystemExit(1)

    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def backup_filename(source: Path, now: datetime, fmt: str = DEFAULT_BACKUP_FORMAT) -> str:
    """Build backup name: e.g. mon_1602_21-02-2026_filename.ext"""
    return f"{now.strftime(fmt)}_{source.name}"


def parse_backup_datetime(date_prefix: str, fmt: str = DEFAULT_BACKUP_FORMAT) -> datetime | None:
    """Parse datetime from the date prefix of a backup filename."""
    try:
        return datetime.strptime(date_prefix, fmt)
    except ValueError:
        return None


def get_backup_dir(destination: Path, source: Path) -> Path:
    """Subfolder named after the source file (no extension, spaces to underscores)."""
    return destination / source.stem.replace(" ", "_")


def existing_backups(
    backup_dir: Path, source_name: str, fmt: str = DEFAULT_BACKUP_FORMAT
) -> list[tuple[Path, datetime]]:
    """Return existing backups for a source file, newest first."""
    backups = []
    if not backup_dir.exists():
        return backups
    suffix = f"_{source_name}"
    for f in backup_dir.iterdir():
        if not f.is_file() or not f.name.endswith(suffix):
            continue
        date_prefix = f.name[: -len(suffix)]
        dt = parse_backup_datetime(date_prefix, fmt)
        if dt:
            backups.append((f, dt))
    backups.sort(key=lambda x: x[1], reverse=True)
    return backups


def needs_backup(backups: list[tuple[Path, datetime]], frequency: str, now: datetime) -> bool:
    """Check whether the most recent backup is older than the interval."""
    if not backups:
        return True
    return (now - backups[0][1]) >= INTERVALS[frequency]


def prune_backups(backups: list[tuple[Path, datetime]], copies: int) -> None:
    """Remove oldest backups that exceed the copy limit."""
    for path, _ in backups[copies:]:
        path.unlink()
        log.info("Pruned old backup: %s", path.name)
        print(f"  Pruned old backup: {path.name}")


def setup_logging(destination: Path) -> None:
    """Configure logging to write to vs_backup.log in the destination folder."""
    destination.mkdir(parents=True, exist_ok=True)
    log_file = destination / "vs_backup.log"
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log.addHandler(handler)
    log.setLevel(logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Back up files per config schedule")
    parser.add_argument(
        "--force", action="store_true", help="Force backup regardless of schedule"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    destination = Path(config["backup_destination"])
    backup_fmt = config.get("backup_format", DEFAULT_BACKUP_FORMAT)
    setup_logging(destination)
    now = datetime.now()

    if args.force:
        log.info("Force flag set — overriding schedule checks")

    for entry in config["files"]:
        source = Path(entry["path"])
        frequency = entry["frequency"]
        copies = entry["copies"]

        if frequency not in INTERVALS:
            msg = f"Unknown frequency '{frequency}' for {source}, skipping"
            log.warning(msg)
            print(f"Warning: {msg}")
            continue

        if not source.exists():
            msg = f"Source file not found: {source}"
            log.warning(msg)
            print(f"Warning: {msg}")
            continue

        backup_dir = get_backup_dir(destination, source)
        backups = existing_backups(backup_dir, source.name, backup_fmt)

        if args.force or needs_backup(backups, frequency, now):
            backup_dir.mkdir(parents=True, exist_ok=True)
            dest_file = backup_dir / backup_filename(source, now, backup_fmt)
            if dest_file.exists():
                log.info("Replacing existing backup: %s", dest_file.name)
                print(f"  Replacing existing backup: {dest_file.name}")
            try:
                shutil.copy2(source, dest_file)
            except OSError as e:
                msg = f"Failed to back up {source}: {e}"
                log.error(msg)
                print(msg)
                continue

            log.info("Backed up: %s -> %s", source.name, dest_file)
            print(f"Backed up: {source.name} -> {dest_file}")

            backups = existing_backups(backup_dir, source.name, backup_fmt)
            prune_backups(backups, copies)
        else:
            log.info("Skipped (recent backup exists): %s", source.name)
            print(f"Skipped (recent backup exists): {source.name}")


if __name__ == "__main__":
    main()
