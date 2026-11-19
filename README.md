# Paid for What? How NBA Salaries Track Performance

DS 325 Final Project, Fall 2026 · Gytis Gervickas · _teammate_ · _teammate_

**Question:** What does the NBA pay for, and who is over- or underpaid?
**Data:** Basketball-Reference.com, 2015-16 → 2025-26, scraped by us (5,968 player-seasons).

**Checkpoint summary:** [reports/EDA_checkpoint_report.md](reports/EDA_checkpoint_report.md) (PDF alongside)

## Layout

| Path | What |
|---|---|
| `src/` | scraper, parser, dataset builder, feature engineering |
| `notebooks/01–03` | data collection · EDA · feature engineering & selection |
| `data/raw`, `data/processed` | curated CSVs ([data dictionary](data/DATA_DICTIONARY.md)) |
| `reports/` | checkpoint report and figures |

## Run

```bash
pip install -r requirements.txt
python src/download.py && python src/parse_bref.py && python src/build_dataset.py   # optional: data is committed
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
python reports/build_report.py
```

> Data: Sports Reference LLC, *Basketball-Reference.com*, https://www.basketball-reference.com/ (accessed Nov 2026).

**AI use:** Claude AI (Anthropic) was used for setting up the GitHub repository and for code edits.
