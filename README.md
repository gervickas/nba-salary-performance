# Paid for What? Measuring How NBA Salaries Track On-Court Performance

DS 325 Final Project, Fall 2026, Gettysburg College

**Team:**
- Gytis Gervickas
- _teammate name_
- _teammate name_

## Research question

Which measurable parts of performance does the NBA labor market actually pay for, and which players are over- or underpaid relative to their production?

1. **Market-value model.** Predict a player's salary (as a share of the salary cap) from information available *before* the season: previous-season production, age, experience, physical profile, and draft pedigree.
2. **Surplus value.** Actual pay minus model-predicted pay gives a per-player over/underpaid measure.
3. **Team level.** Do teams that collect more surplus value win more, controlling for payroll?

**Who would use it:** front offices and agents (contract negotiation benchmarks), fantasy and media analysts (value rankings), and fans and reporters who want to judge contract quality with evidence.

## Data

Source: **Basketball-Reference.com** (Sports Reference LLC), seasons **2015-16 through 2025-26**, all 30 teams. It was collected by our own scraper (`src/download.py`), rate-limited to respect Sports Reference's 20-requests-per-minute rule.

| Table | Grain |
|---|---|
| Per-game and advanced stats | player × season |
| Salaries, rosters (height, weight, experience), team records | player × season × team (from 330 team-season pages) |
| Draft history, 1990–2025 | player |
| Salary cap history | season |

All joins use Basketball-Reference player ids (e.g. `curryst01`), so there is no fuzzy name matching. The curated CSVs are committed in `data/raw/` and `data/processed/`.

> Sports Reference LLC. *Basketball-Reference.com: Basketball Statistics and History.* https://www.basketball-reference.com/ (accessed November 2026).

## Repository layout

```
src/
  download.py          # step 1: download pages into data/cache/ (gitignored)
  parse_bref.py        # step 2: HTML -> tidy CSVs in data/raw/
  build_dataset.py     # step 3: join -> data/processed/player_seasons.csv
  features.py          # feature engineering (used by notebooks 02 and 03)
  plotting.py          # shared figure style
notebooks/
  01_data_collection.ipynb               # sources, collection, curation decisions
  02_eda.ipynb                           # exploratory data analysis
  03_feature_engineering_selection.ipynb # features, selection, modeling-readiness check
data/
  raw/                 # parsed source tables
  processed/           # player_seasons.csv, model_table.csv, selected_features.json
reports/
  figures/             # all figures, saved by the notebooks
  EDA_checkpoint_report.pdf
```

## Reproducing

```bash
pip install -r requirements.txt
python src/download.py        # ~45 min (polite crawl delay); skips pages already cached
python src/parse_bref.py
python src/build_dataset.py
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

The processed data is already committed, so the notebooks run without re-scraping.

## Status (EDA checkpoint, Nov 18 2026)

- [x] Data collection and curation
- [x] Exploratory data analysis
- [x] Feature engineering and feature selection
- [ ] Model training and tuning (market-value model)
- [ ] Surplus-value analysis and team-level question
- [ ] Final report (ACM SIGCHI format) and presentation
