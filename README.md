# BluePort AI — Field Testing

Practical repository to run **on-the-ground tests** with mobile photos for marine/port waste detection.  
Use it to centralize guides, data, and quick analysis toward a future drone/camera pipeline.

## Repository Structure
```
blueport-ai-field/
├── README.md
├── guides/
│   └── blueport_field_guide.pdf
├── data/
│   ├── raw/          # original photos (keep EXIF when possible)
│   ├── processed/    # cleaned/cropped/resized images
│   └── logs/         # CSV exports from the Waste Bot
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_visualization.ipynb
│   └── 03_training.ipynb
├── scripts/
│   └── export_cleaner.py
└── assets/
    └── blueport_logo.svg
```

## Quick Start
1. Use your **Telegram Waste Bot** (from BluePort AI) to take phone photos and classify items.
2. Export logs with `/export` and place CSVs into `data/logs/`.
3. Move photos into `data/raw/` following a consistent naming scheme, e.g.:
   `YYYYMMDD_location_class_###.jpg`

## Recommended Log Columns
- `timestamp_utc` (ISO 8601), `location` (pier/berth/channel), `class`, `confidence` (0–1), `feedback_correct` (0/1/NA)

## Next Steps
- Run notebooks for simple analytics (counts, accuracy, per-location charts).
- Prepare a small labeled set (300–500 images) for detector training (YOLOv8/CLIP fine-tune).
- Evolve to pier cameras and drone surveys.


## Field Dashboard (Streamlit)
Run a quick dashboard to visualize your logs and hotspots:

```bash
pip install -r requirements_dashboard.txt
streamlit run streamlit_app.py
```

- Place cleaned logs in `data/logs/` (e.g., `waste_history_clean.csv`).
- Edit `assets/locations.csv` with your pier/berth/channel coordinates to enable the map.
