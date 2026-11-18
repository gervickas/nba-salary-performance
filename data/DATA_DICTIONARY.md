# Data dictionary — `data/processed/player_seasons.csv`

5,968 rows (one per player-season), 71 columns. Source: Basketball-Reference.com.
Engineered model features are created in `src/features.py` and documented in notebook 03.

| Column | Description | Non-missing |
|---|---|---|
| `season` | Season end year (2016 = 2015-16) | 100% |
| `player_id` | Basketball-Reference player id (join key) | 100% |
| `player` | Player name | 100% |
| `age` | Age on Feb 1 of the season | 100% |
| `team` | Team abbreviation, or 2TM/3TM/... for players traded mid-season | 100% |
| `pos` | Listed position | 100% |
| `g` | Games played | 100% |
| `gs` | Games started | 100% |
| `mp_per_g` | Minutes per game | 100% |
| `fg` | Field goals made per game | 100% |
| `fga` | Field goal attempts per game | 100% |
| `fg_pct` | Field goal % | 99% |
| `fg3` | 3-pointers made per game | 100% |
| `fg3a` | 3-point attempts per game | 100% |
| `fg3_pct` | 3-point % | 94% |
| `fg2` | 2-pointers made per game | 100% |
| `fg2a` | 2-point attempts per game | 100% |
| `fg2_pct` | 2-point % | 99% |
| `efg_pct` | Effective field goal % | 99% |
| `ft` | Free throws made per game | 100% |
| `fta` | Free throw attempts per game | 100% |
| `ft_pct` | Free throw % | 95% |
| `orb` | Offensive rebounds per game | 100% |
| `drb` | Defensive rebounds per game | 100% |
| `trb` | Total rebounds per game | 100% |
| `ast` | Assists per game | 100% |
| `stl` | Steals per game | 100% |
| `blk` | Blocks per game | 100% |
| `tov` | Turnovers per game | 100% |
| `pf` | Personal fouls per game | 100% |
| `pts` | Points per game | 100% |
| `awards` | Award voting / honors string (e.g. MVP-1,AS,NBA1) | 10% |
| `n_teams` | Number of teams played for that season | 100% |
| `final_team` | Last team played for that season | 100% |
| `mp_total` | Total minutes played | 100% |
| `per` | Player Efficiency Rating | 100% |
| `ts_pct` | True shooting % | 100% |
| `fg3a_rate` | 3-point attempt rate (3PA / FGA) | 99% |
| `fta_rate` | Free throw rate (FTA / FGA) | 99% |
| `orb_pct` | Offensive rebound % | 100% |
| `drb_pct` | Defensive rebound % | 100% |
| `trb_pct` | Total rebound % | 100% |
| `ast_pct` | Assist % | 100% |
| `stl_pct` | Steal % | 100% |
| `blk_pct` | Block % | 100% |
| `tov_pct` | Turnover % | 100% |
| `usg_pct` | Usage % | 100% |
| `ows` | Offensive win shares | 100% |
| `dws` | Defensive win shares | 100% |
| `ws` | Win shares | 100% |
| `ws_per_48` | Win shares per 48 minutes | 100% |
| `obpm` | Offensive box plus/minus | 100% |
| `dbpm` | Defensive box plus/minus | 100% |
| `bpm` | Box plus/minus | 100% |
| `vorp` | Value over replacement player | 100% |
| `n_salary_teams` | Number of team salary tables listing the player | 91% |
| `salary` | Season salary in USD (see curation rules in notebook 01) | 91% |
| `salary_source` | team_played_for, or other_listing (fallback) | 91% |
| `height_in` | Height in inches | 100% |
| `weight` | Weight in lbs | 100% |
| `birth_date` | Birth date | 100% |
| `years_experience` | Prior NBA seasons (0 = rookie) | 100% |
| `college` | College | 86% |
| `draft_year` | Draft year (blank if undrafted) | 75% |
| `pick_overall` | Overall draft pick (blank if undrafted) | 75% |
| `salary_cap` | League salary cap for the season (USD) | 100% |
| `wins` | Final team's wins | 100% |
| `losses` | Final team's losses | 100% |
| `team_win_pct` | Final team's win % | 100% |
| `salary_pct_cap` | salary / salary_cap (modeling target before log) | 91% |
| `has_salary` | True if a salary record was found | 100% |
