#!/usr/bin/env python3
"""
export_cleaner.py — tidy up CSV logs from the Waste Bot.
Usage:
  python scripts/export_cleaner.py data/logs/waste_history.csv data/logs/waste_history_clean.csv --location "Pier 1"
- Normalizes header names
- Adds 'location' if provided
- Ensures ISO-8601 timestamps
"""
import csv, argparse, datetime as dt

def iso(s):
    try:
        # pass through if already ISO-like
        if 'T' in s and 'Z' in s:
            return s
        # fallback: parse common patterns
        return dt.datetime.fromisoformat(s).replace(microsecond=0).isoformat() + 'Z'
    except Exception:
        return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_csv')
    ap.add_argument('output_csv')
    ap.add_argument('--location', default=None, help='e.g., Pier 1, Berth 3, Channel A')
    args = ap.parse_args()

    rows = []
    with open(args.input_csv, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            out = {}
            # map common fields
            out['timestamp_utc'] = iso(row.get('ts_utc') or row.get('timestamp') or row.get('time') or '')
            out['class'] = row.get('label') or row.get('class') or ''
            out['confidence'] = row.get('confidence') or row.get('score') or ''
            fb = row.get('feedback_correct')
            out['feedback_correct'] = fb if fb in ('0','1') else ''
            if args.location:
                out['location'] = args.location
            rows.append(out)

    with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['timestamp_utc','location','class','confidence','feedback_correct'])
        w.writeheader()
        for r in rows:
            if 'location' not in r:
                r['location'] = ''
            w.writerow(r)

if __name__ == '__main__':
    main()
