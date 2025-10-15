#!/usr/bin/env python3

import os, glob, subprocess, sys

INBOX = "exports_inbox"
OUTDIR = "data/logs"

def main():
    os.makedirs(INBOX, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(INBOX, "*.csv")))
    if not files:
        print("No CSVs in exports_inbox/. Place your Telegram bot export here.")
        return
    latest = files[-1]
    out = os.path.join(OUTDIR, os.path.basename(latest).replace(".csv","_clean.csv"))
    print(f"Cleaning {latest} -> {out}")
    subprocess.run([sys.executable, "scripts/export_cleaner.py", latest, out, "--location", "Pier 1"], check=True)

if __name__ == "__main__":
    main()
