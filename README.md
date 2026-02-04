# vs_backup

Extremely simple scheduled file backup tool. Copies files to a destination folder based on a configurable frequency, keeping a set number of rolling copies.

## Configure

On first run a sample config is created at the platform config directory:

- Windows: `%LOCALAPPDATA%\vs_backup\config.toml`
- macOS: `~/Library/Application Support/vs_backup/config.toml`
- Linux: `~/.config/vs_backup/config.toml`

Example config:

```toml
backup_destination = "D:/Backups"

[[files]]
path = "C:/Users/tom/Documents/myimportantspreadsheet.xlsx"
frequency = "daily"
copies = 7

[[files]]
path = "C:/Users/tom/Documents/contacts.csv"
frequency = "weekly"
copies = 4
```

| Key | Description |
|-----|-------------|
| `backup_destination` | Folder where backups are stored |
| `path` | Absolute path to the source file |
| `frequency` | `hourly`, `daily`, or `weekly` |
| `copies` | Number of rolling backups to keep |
| `backup_format` | *(optional)* [strftime format](https://strftime.org/) for filename **prefix**, default `%a_%H%M_%d-%m-%Y` |

Backup filenames are `{format}_{filename}`, e.g. `Wed_1602_21-02-2026_myimportantspreadsheet.xlsx`.

## Run with uv

```
uv run vs_file_backup.py
uv run vs_file_backup.py --force
```

## Install the executable

Download `vs_backup.exe` from the [latest release](../../releases/latest) and
place it anywhere on your PATH.

This is provided just to avoid issues with finding uv/python if run by task
scheduler etc.

```
vs_backup
vs_backup --force
```
