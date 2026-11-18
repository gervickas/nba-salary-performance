"""Parse cached Basketball-Reference pages (data/cache/*.html.gz) into tidy CSVs in data/raw/.

Outputs
  per_game.csv   one row per player-season-team stint (per-game box score stats)
  advanced.csv   one row per player-season-team stint (PER, WS, BPM, VORP, ...)
  salaries.csv   one row per player-season-team (salary listed on that team's page)
  rosters.csv    one row per player-season-team (height, weight, experience, birth date)
  teams.csv      one row per team-season (wins, losses)
  draft.csv      one row per drafted player (draft year, overall pick)
  salary_cap.csv one row per season (league salary cap)

Usage:  python src/parse_bref.py
"""
import gzip
import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from download import CACHE, DRAFT_YEARS, SEASONS, TEAMS

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PLAYER_HREF = re.compile(r"/players/[a-z]/([a-z0-9]+)\.html")


def read_cached(name):
    path = CACHE / name
    if not path.exists():
        return None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        # Sports Reference hides secondary tables inside HTML comments.
        return fh.read().replace("<!--", "").replace("-->", "")


def parse_table(html, table_id):
    """Return a DataFrame keyed by each cell's data-stat name, plus player_id."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id=table_id)
    if table is None:
        return pd.DataFrame()
    trs = table.tbody.find_all("tr") if table.tbody else table.find_all("tr")
    rows = []
    for tr in trs:
        if "thead" in (tr.get("class") or []) or tr.find_parent("thead") is not None:
            continue
        row = {}
        for cell in tr.find_all(["th", "td"]):
            stat = cell.get("data-stat")
            if not stat:
                continue
            row[stat] = cell.get_text(strip=True)
            pid = cell.get("data-append-csv")
            if pid is None and cell.a is not None:
                m = PLAYER_HREF.search(cell.a.get("href", ""))
                pid = m.group(1) if m else None
            if pid and "player_id" not in row:
                row["player_id"] = pid
            if stat == "height" and cell.get("csk"):
                row["height_in"] = cell["csk"]
        rows.append(row)
    return pd.DataFrame(rows)


def money(s):
    return pd.to_numeric(s.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")


def parse_league(kind):
    frames = []
    for yr in SEASONS:
        html = read_cached(f"{kind}_{yr}.html.gz")
        if html is None:
            print(f"missing {kind}_{yr}")
            continue
        df = parse_table(html, "per_game_stats" if kind == "per_game" else "advanced")
        df = df[df["player_id"].notna()].copy()
        df.insert(0, "season", yr)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def parse_teams():
    salaries, rosters, teams = [], [], []
    for yr in SEASONS:
        for team in TEAMS:
            html = read_cached(f"team_{team}_{yr}.html.gz")
            if html is None:
                print(f"missing team_{team}_{yr}")
                continue
            sal = parse_table(html, "salaries2")
            if not sal.empty:
                sal = sal[sal["player_id"].notna()][["player_id", "player", "salary"]].copy()
                sal["salary"] = money(sal["salary"])
                sal.insert(0, "team", team)
                sal.insert(0, "season", yr)
                salaries.append(sal)
            ros = parse_table(html, "roster")
            if not ros.empty:
                keep = [c for c in ["player_id", "player", "pos", "height", "height_in", "weight",
                                    "birth_date", "years_experience", "college"] if c in ros]
                ros = ros[ros["player_id"].notna()][keep].copy()
                ros.insert(0, "team", team)
                ros.insert(0, "season", yr)
                rosters.append(ros)
            m = re.search(r"<strong>Record:</strong>\s*(\d+)-(\d+)", html)
            if m:
                teams.append({"season": yr, "team": team,
                              "wins": int(m.group(1)), "losses": int(m.group(2))})
    return (pd.concat(salaries, ignore_index=True), pd.concat(rosters, ignore_index=True),
            pd.DataFrame(teams))


def parse_draft():
    frames = []
    for yr in DRAFT_YEARS:
        html = read_cached(f"draft_{yr}.html.gz")
        if html is None:
            print(f"missing draft_{yr}")
            continue
        df = parse_table(html, "stats")
        df = df[df["player_id"].notna()][["player_id", "player", "pick_overall", "team_id", "college_name"]]
        df.insert(0, "draft_year", yr)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["pick_overall"] = pd.to_numeric(out["pick_overall"], errors="coerce")
    return out


def parse_cap():
    df = parse_table(read_cached("salary_cap.html.gz"), "salary_cap_history")
    df = df[df["year_id"].str.match(r"^\d{4}-\d{2}$", na=False)].copy()
    df["season"] = df["year_id"].str[:4].astype(int) + 1   # "2015-16" -> 2016
    df["salary_cap"] = money(df["cap"])
    return df[["season", "year_id", "salary_cap"]]


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    outputs = {"per_game": parse_league("per_game"), "advanced": parse_league("advanced")}
    outputs["salaries"], outputs["rosters"], outputs["teams"] = parse_teams()
    outputs["draft"] = parse_draft()
    outputs["salary_cap"] = parse_cap()
    for name, df in outputs.items():
        df.to_csv(RAW / f"{name}.csv", index=False)
        print(f"{name:11s} {df.shape}")


if __name__ == "__main__":
    main()
