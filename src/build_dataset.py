"""Merge the raw tables into one row per player-season: data/processed/player_seasons.csv.

Join keys are Basketball-Reference player ids (e.g. "curryst01"), so no fuzzy
name matching is needed. Players traded mid-season appear on several team
pages; we keep their combined-season stat line ("2TM"/"3TM" rows), take their
salary as the max listed across teams, and assign them to the last team they
played for.

Usage:  python src/build_dataset.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
MULTI_TEAM = r"^(TOT|\dTM)$"

PER_GAME_COLS = {
    "name_display": "player", "age": "age", "team_name_abbr": "team", "pos": "pos",
    "games": "g", "games_started": "gs", "mp_per_g": "mp_per_g",
    "fg_per_g": "fg", "fga_per_g": "fga", "fg_pct": "fg_pct",
    "fg3_per_g": "fg3", "fg3a_per_g": "fg3a", "fg3_pct": "fg3_pct",
    "fg2_per_g": "fg2", "fg2a_per_g": "fg2a", "fg2_pct": "fg2_pct", "efg_pct": "efg_pct",
    "ft_per_g": "ft", "fta_per_g": "fta", "ft_pct": "ft_pct",
    "orb_per_g": "orb", "drb_per_g": "drb", "trb_per_g": "trb", "ast_per_g": "ast",
    "stl_per_g": "stl", "blk_per_g": "blk", "tov_per_g": "tov", "pf_per_g": "pf",
    "pts_per_g": "pts", "awards": "awards",
}
ADV_COLS = {
    "mp": "mp_total", "per": "per", "ts_pct": "ts_pct", "fg3a_per_fga_pct": "fg3a_rate",
    "fta_per_fga_pct": "fta_rate", "orb_pct": "orb_pct", "drb_pct": "drb_pct",
    "trb_pct": "trb_pct", "ast_pct": "ast_pct", "stl_pct": "stl_pct", "blk_pct": "blk_pct",
    "tov_pct": "tov_pct", "usg_pct": "usg_pct", "ows": "ows", "dws": "dws", "ws": "ws",
    "ws_per_48": "ws_per_48", "obpm": "obpm", "dbpm": "dbpm", "bpm": "bpm", "vorp": "vorp",
}


def one_row_per_player(df, cols):
    """Collapse per-team stints to one season line; record team count and final team."""
    df = df.rename(columns=cols)[["season", "player_id", *cols.values()]].copy()
    df["_order"] = np.arange(len(df))
    is_total = df["team"].str.match(MULTI_TEAM, na=False) if "team" in df else False
    stints = df[~is_total] if "team" in df else df
    meta = (stints.sort_values("_order").groupby(["season", "player_id"])
            .agg(n_teams=("team", "nunique"), final_team=("team", "last"))
            .reset_index()) if "team" in df else None
    # Keep the combined row when it exists, otherwise the single stint.
    df["_is_total"] = is_total
    df = (df.sort_values(["season", "player_id", "_is_total", "_order"],
                         ascending=[True, True, False, True])
            .drop_duplicates(["season", "player_id"]))
    df = df.drop(columns=["_order", "_is_total"])
    if meta is not None:
        df = df.merge(meta, on=["season", "player_id"], how="left")
    return df


def to_numeric(df, skip):
    for c in df.columns:
        if c not in skip:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    per_game = pd.read_csv(RAW / "per_game.csv", dtype=str)
    advanced = pd.read_csv(RAW / "advanced.csv", dtype=str)
    salaries = pd.read_csv(RAW / "salaries.csv")
    rosters = pd.read_csv(RAW / "rosters.csv", dtype=str)
    teams = pd.read_csv(RAW / "teams.csv")
    draft = pd.read_csv(RAW / "draft.csv")
    cap = pd.read_csv(RAW / "salary_cap.csv")

    for d in (per_game, advanced):
        d["season"] = d["season"].astype(int)
    stats = one_row_per_player(per_game, PER_GAME_COLS)
    adv = one_row_per_player(advanced.assign(team=advanced["team_name_abbr"]),
                             {**ADV_COLS, "team": "team"}).drop(columns=["team", "n_teams", "final_team"])
    stats = stats.merge(adv, on=["season", "player_id"], how="left")
    stats = to_numeric(stats, skip={"player_id", "player", "team", "pos", "awards", "final_team"})

    # Team salary tables also carry dead money for waived players, so prefer the salary
    # listed by a team the player actually played for; fall back to any listing.
    # $0 listings are two-way contracts with no recorded amount -- treat as missing.
    salaries = salaries[salaries["salary"] > 0]
    stints = (per_game.loc[~per_game["team_name_abbr"].str.match(MULTI_TEAM, na=False),
                           ["season", "player_id", "team_name_abbr"]]
              .rename(columns={"team_name_abbr": "team"}).drop_duplicates())
    played = (salaries.merge(stints, on=["season", "player_id", "team"])
              .groupby(["season", "player_id"]).salary.max().rename("salary_played"))
    sal = (salaries.groupby(["season", "player_id"])
           .agg(salary_any=("salary", "max"), n_salary_teams=("team", "nunique"))
           .join(played).reset_index())
    sal["salary"] = sal["salary_played"].fillna(sal["salary_any"])
    sal["salary_source"] = np.where(sal["salary_played"].notna(), "team_played_for", "other_listing")
    sal = sal.drop(columns=["salary_any", "salary_played"])

    rosters["season"] = rosters["season"].astype(int)
    ros = (rosters.drop_duplicates(["season", "player_id"])
           [["season", "player_id", "height_in", "weight", "birth_date", "years_experience", "college"]]
           .copy())
    ros["years_experience"] = pd.to_numeric(ros["years_experience"].replace("R", "0"), errors="coerce")
    ros["height_in"] = pd.to_numeric(ros["height_in"], errors="coerce")
    ros["weight"] = pd.to_numeric(ros["weight"], errors="coerce")

    drf = (draft.sort_values("draft_year").drop_duplicates("player_id")
           [["player_id", "draft_year", "pick_overall"]])

    teams["team_win_pct"] = teams["wins"] / (teams["wins"] + teams["losses"])

    df = (stats.merge(sal, on=["season", "player_id"], how="left")
               .merge(ros, on=["season", "player_id"], how="left")
               .merge(drf, on="player_id", how="left")
               .merge(cap[["season", "salary_cap"]], on="season", how="left")
               .merge(teams.rename(columns={"team": "final_team"}),
                      on=["season", "final_team"], how="left"))

    df["salary_pct_cap"] = df["salary"] / df["salary_cap"]
    df["has_salary"] = df["salary"].notna()
    df = df.sort_values(["season", "player_id"]).reset_index(drop=True)
    df.to_csv(OUT / "player_seasons.csv", index=False)

    print(f"player-seasons with stats:  {len(df):,}")
    print(f"  ...with a salary record:  {df['has_salary'].sum():,} ({df['has_salary'].mean():.1%})")
    print(f"unique players:             {df['player_id'].nunique():,}")
    print(df.groupby("season")["has_salary"].agg(["size", "sum"]).rename(columns={"size": "players", "sum": "with_salary"}))


if __name__ == "__main__":
    main()
