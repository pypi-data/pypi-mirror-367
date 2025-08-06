```bash
Def: pkg-log-search is a CLI tool to filter structured tab-delimited log files

usage: pkg-log-search [-h] --logfile LOGFILE [--from START] [--to END] [--level LEVEL] [--module MODULE] [--regex REGEX]

Filter structured log files.

options:
  -h, --help         show this help message and exit
  --logfile LOGFILE  Path to log file
  --from START       Start datetime (e.g. '2025-07-28 00:00:00')
  --to END           End datetime (e.g. '2025-07-28 23:59:59')
  --level LEVEL      Log level (e.g. INFO, ERROR, WARNING)
  --module MODULE    Filter by module name
  --regex REGEX      Regex pattern in message


## 🚀 Example Usage
```bash
usage examples:

# Filter by log level
package-log-search --logfile logs/pipeline.log --level ERROR

# Filter by date range
package-log-search --logfile logs/pipeline.log \
  --from "2025-07-28 00:00:00" \
  --to "2025-07-28 23:59:59"

# Filter by module name
package-log-search --logfile logs/pipeline.log --module ingest

# Filter by regex pattern in message
package-log-search --logfile logs/pipeline.log --regex "failed.*attempt"

# Combine all filters
package-log-search --logfile logs/pipeline.log \
  --from "2025-07-28 00:00:00" \
  --to "2025-07-28 23:59:59" \
  --level ERROR \
  --module transform \
  --regex "skipped.*\.json"
