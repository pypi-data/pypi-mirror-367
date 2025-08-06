
---

## Features

* **Deduplicated Logging:** Prevents duplicate log entries within each log file, keeping your logs concise and clean.
* **Per-Level Log Files:** Saves log entries to separate files by level (`Debug.txt`, `Info.txt`, `Warning.txt`, `Error.txt`, `Critical.txt`) for easy tracking and analysis.
* **Automatic Log Cleanup:** Periodically purges log entries older than your retention window (default: 24 hours), with full customization.
* **Thread-Safe:** All logging and cleanup operations are safe for multi-threaded environments.
* **Console Output:** Only errors and critical logs are printed to the console by default, with consistent formatting.
* **Flexible Integration:** Just call `HoloLog(logsDir)` and start logging—no need to rewrite your codebase.

---

## Installation

```bash
pip install HoloLog
```

---

## Quick Start

```python
from HoloLog import HoloLog
from pathlib import Path
import logging

# Initialize HoloLog (set your desired logs directory)
logsDir = Path("logs")
HoloLog(logsDir)

logger = logging.getLogger(__name__)

# Use standard logging
def loggingErrorTest():
    try:
        # Simulate an error for testing
        raise ValueError("This is a test error for logging.")
    except Exception as e:
        logger.error(f"An error occurred", exc_info=True)
```

---

## How It Works

* **Deduplication:**
  HoloLog compares each new log entry (except the timestamp/level prefix) to recent entries in its level’s file and writes only unique messages.
* **Cleanup:**
  Log files are automatically cleaned in the background, keeping only entries within your retention window (default: 24 hours, configurable with `LOG_RETENTION_HOURS` in your `.env` or environment).
* **Retention:**
  Customize how long logs are kept by setting the `LOG_RETENTION_HOURS` environment variable.

---

## Configuration

* **Log Directory:**
  Pass any `Path` to `HoloLog()`. Directory will be created if missing.

* **Log Retention:**
  Set the number of hours to keep log entries:

  ```
  LOG_RETENTION_HOURS=48
  ```

  (in your `.env` or system environment)

* **Threaded Cleanup:**
  HoloLog launches a daemon thread to clean logs every hour. No user intervention needed.

---

## Advanced Usage

* **Multiple Loggers:**
  All loggers in your app will use the same log directory and handlers by default.

---

## Notes

* HoloLog is compatible with Python 3.8+ and all standard `logging` calls.
* Log file deduplication works at the message-body level for maximum efficiency.
* HoloLog is optimized for long-running, high-traffic, or mission-critical systems.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil

