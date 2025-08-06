import argparse
import re
from datetime import datetime

LOG_FORMAT = "%Y-%m-%d %H:%M:%S"

def parse_log_line(line):
    try:
        date_str, level, module, message = line.strip().split("\t", 3)
        date = datetime.strptime(date_str, LOG_FORMAT)
        return {"date": date, "level": level, "module": module, "message": message}
    except ValueError:
        return None

def search_logs(filepath, start=None, end=None, level=None, module=None, regex=None):
    try:
        with open(filepath, "r") as f:
            for line in f:
                log = parse_log_line(line)
                if not log:
                    continue

                if start and log["date"] < start:
                    continue
                if end and log["date"] > end:
                    continue
                if level and log["level"].lower() != level.lower():
                    continue
                if module and module.lower() not in log["module"].lower():
                    continue
                if regex and not re.search(regex, log["message"]):
                    continue

                print(f'{log["date"].strftime(LOG_FORMAT)}\t{log["level"]}\t{log["module"]}\t{log["message"]}')
    except FileNotFoundError:
        print(f"❌ Log file not found: {filepath}")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Filter structured log files.")
    parser.add_argument("--logfile", required=True, help="Path to log file")
    parser.add_argument("--from", dest="start", help="Start datetime (e.g. '2025-07-28 00:00:00')")
    parser.add_argument("--to", dest="end", help="End datetime (e.g. '2025-07-28 23:59:59')")
    parser.add_argument("--level", help="Log level (e.g. INFO, ERROR, WARNING)")
    parser.add_argument("--module", help="Filter by module name")
    parser.add_argument("--regex", help="Regex pattern in message")

    args = parser.parse_args()

    start = datetime.strptime(args.start, LOG_FORMAT) if args.start else None
    end = datetime.strptime(args.end, LOG_FORMAT) if args.end else None

    search_logs(
        filepath=args.logfile,
        start=start,
        end=end,
        level=args.level,
        module=args.module,
        regex=args.regex
    )

if __name__ == "__main__":
    main()

