"""Feature engineering for the salary-vs-performance model.

Salary for season t is mostly set by contracts signed *before* season t, so the
main performance features are lagged (previous-season) values. Same-season
stats are kept too, because the final "surplus value" analysis compares pay
with production in the same season.
"""
import numpy as np
import pandas as pd

POS_GROUP = {"PG": "Guard", "SG": "Guard", "SF": "Forward", "PF": "Forward", "C": "Center"}
PER36 = ["pts", "trb", "ast", "stl", "blk", "tov", "fg3", "fta"]
LAG = ["pts", "trb", "ast", "mp_per_g", "g", "gs", "mp_total", "per", "ts_pct", "usg_pct",
       "ws", "ws_per_48", "obpm", "dbpm", "bpm", "vorp", "availability", "pts_per36",
       "all_star", "all_nba"]
RATE = ["per", "ts_pct", "usg_pct", "ws_per_48", "obpm", "dbpm", "bpm", "pts_per36"]
MIN_MINUTES = 250
SHRINK_MINUTES = 250


def shrink_rates(df):
    """Pull small-sample rate stats toward the season's minutes-weighted league mean.

    shrunk = (x * MP + mean * K) / (MP + K), K = 250 minutes, so a 20-minute season with
    a PER of 60 ends up near league average while a 2,000-minute season barely moves.
    """
    mp = df["mp_total"].fillna(0)
    for c in RATE:
        valid = df[c].notna() & (mp > 0)
        w_mean = (df.loc[valid, c] * mp[valid]).groupby(df.loc[valid, "season"]).sum() \
            / mp[valid].groupby(df.loc[valid, "season"]).sum()
        mu = df["season"].map(w_mean)
        df[c] = (df[c].fillna(mu) * mp + mu * SHRINK_MINUTES) / (mp + SHRINK_MINUTES)
    return df


def build_features(df):
    df = df.sort_values(["player_id", "season"]).copy()

    df["log_salary_pct_cap"] = np.log(df["salary_pct_cap"])
    df["pos_group"] = df["pos"].str.split("-").str[0].map(POS_GROUP)

    safe_mp = df["mp_per_g"].where(df["mp_per_g"] > 0)
    for c in PER36:
        df[f"{c}_per36"] = df[c] / safe_mp * 36

    team_games = (df["wins"] + df["losses"]).fillna(82)
    df["availability"] = (df["g"] / team_games).clip(upper=1)
    df["start_rate"] = df["gs"] / df["g"].where(df["g"] > 0)

    awards = df["awards"].fillna("")
    df["all_star"] = awards.str.contains(r"\bAS\b").astype(int)
    df["all_nba"] = awards.str.contains(r"\bNBA[123]\b").astype(int)

    raw_rates = df[RATE].add_suffix("_raw")
    df = pd.concat([shrink_rates(df), raw_rates], axis=1)

    df["age_sq"] = df["age"] ** 2
    df["undrafted"] = df["pick_overall"].isna().astype(int)
    df["first_round"] = (df["pick_overall"] <= 30).astype(int)
    # Rookie deals run four seasons from the draft; the draft-year bound stops players who missed
    # seasons (low experience count, e.g. Ben Simmons) from being kept on the scale after extending.
    since_draft = df["season"] - df["draft_year"]
    df["rookie_scale"] = ((df["pick_overall"] <= 30) & (df["years_experience"] <= 3)
                          & since_draft.between(1, 4)).astype(int)
    df["shortened_season"] = df["season"].isin([2020, 2021]).astype(int)

    g = df.groupby("player_id")
    consecutive = (g["season"].diff() == 1)
    for c in LAG:
        df[f"prev_{c}"] = g[c].shift(1).where(consecutive)
    df["has_prev_season"] = consecutive.astype(int)
    consecutive2 = consecutive & (g["season"].diff(2) == 2)
    for c in ["ws", "vorp", "bpm", "mp_total"]:
        prev2 = g[c].shift(2).where(consecutive2)
        df[f"avg2_{c}"] = df[[f"prev_{c}"]].join(prev2.rename("p2")).mean(axis=1, skipna=False)

    # Descriptive only (derived from the target) -- never a model input.
    df["prev_salary_pct_cap"] = g["salary_pct_cap"].shift(1).where(consecutive)
    df["salary_change"] = df["salary_pct_cap"] - df["prev_salary_pct_cap"]

    df["modeling_sample"] = (df["has_salary"] & (df["mp_total"] >= MIN_MINUTES)).astype(int)
    return df.sort_values(["season", "player_id"]).reset_index(drop=True)
