"""
EPL 2025-26 Analysis Engine
Reproduces (in pandas) every query from the original EPL 2024-25 project's
"EPL Queries.sql", applied to the 2025-26 season-2526.csv dataset.

This script exists so the results can be generated and sanity-checked
without a live MySQL server. The accompanying "EPL Queries 2025-26.sql"
file contains the same logic written as real MySQL, for the user to run
in MySQL Workbench against their own imported table.
"""
import pandas as pd
import numpy as np
import os

pd.set_option('display.width', 120)

IN_PATH = 'dataset/premier-league/season-2526.csv'
OUT_DIR = 'csv'
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(IN_PATH, parse_dates=['Date'])
df['Month'] = df['Date'].dt.month

def save(dframe, name, sort_by=None, ascending=False, round_cols=None):
    d = dframe.copy()
    if round_cols:
        for c in round_cols:
            d[c] = d[c].round(2)
    if sort_by:
        d = d.sort_values(sort_by, ascending=ascending)
    path = os.path.join(OUT_DIR, name)
    d.to_csv(path, index=False)
    print(f"  wrote {name:55s} rows={len(d)}")

print(f"Loaded {len(df)} matches, {df['Date'].min().date()} to {df['Date'].max().date()}")
print("Generating 27 analysis CSVs into ./csv/ ...")

# 1. Goal Conversion Rate (goals / shots) per team
home = df.groupby('HomeTeam').agg(total_goals=('FTHG', 'sum'), total_shots=('HS', 'sum')).reset_index().rename(columns={'HomeTeam': 'team'})
away = df.groupby('AwayTeam').agg(total_goals=('FTAG', 'sum'), total_shots=('AS', 'sum')).reset_index().rename(columns={'AwayTeam': 'team'})
conv = pd.concat([home, away]).groupby('team').sum().reset_index()
conv['conversion_rate_percentage'] = (conv['total_goals'] * 100.0 / conv['total_shots']).round(2)
save(conv, 'goalConversionRate_eachTeam.csv', sort_by='conversion_rate_percentage')

# 2. Win/Draw/Loss home vs away
h = df.assign(
    home_wins=(df.FTR == 'H').astype(int), home_draws=(df.FTR == 'D').astype(int), home_losses=(df.FTR == 'A').astype(int)
)[['HomeTeam', 'home_wins', 'home_draws', 'home_losses']].rename(columns={'HomeTeam': 'team'})
a = df.assign(
    away_wins=(df.FTR == 'A').astype(int), away_draws=(df.FTR == 'D').astype(int), away_losses=(df.FTR == 'H').astype(int)
)[['AwayTeam', 'away_wins', 'away_draws', 'away_losses']].rename(columns={'AwayTeam': 'team'})
wdl = h.groupby('team').sum().join(a.groupby('team').sum(), how='outer').reset_index()
save(wdl, 'winDrawLoss_count_eachTeam_atHomeVsAway.csv', sort_by='team', ascending=True)

# 3. Season totals
season_summary = pd.DataFrame([{
    'total_matches': len(df),
    'total_goals': int(df.FTHG.sum() + df.FTAG.sum()),
    'total_home_goals': int(df.FTHG.sum()),
    'total_away_goals': int(df.FTAG.sum()),
    'total_yellow_cards': int(df.HY.sum() + df.AY.sum()),
    'total_red_cards': int(df.HR.sum() + df.AR.sum()),
    'avg_goals_per_match': round((df.FTHG.sum() + df.FTAG.sum()) / len(df), 2),
    'avg_home_goals_per_match': round(df.FTHG.sum() / len(df), 2),
    'avg_away_goals_per_match': round(df.FTAG.sum() / len(df), 2),
}])
save(season_summary, 'totalMatches_goals_yellowRedCards_avgGoals_perMatch.csv')

# 4. Avg fouls/cards per referee
ref = df.groupby('Referee').agg(
    Matches_Officiated=('Referee', 'count'),
    Total_Fouls=('HF', lambda s: (df.loc[s.index, 'HF'] + df.loc[s.index, 'AF']).sum()),
).reset_index()
# simpler/robust approach:
ref = df.assign(fouls=df.HF + df.AF, ycards=df.HY + df.AY, rcards=df.HR + df.AR).groupby('Referee').agg(
    Matches_Officiated=('fouls', 'count'), Total_Fouls=('fouls', 'sum'),
    Total_Yellow_Cards=('ycards', 'sum'), Total_Red_Cards=('rcards', 'sum'),
    Avg_Fouls_Per_Match=('fouls', 'mean'), Avg_Yellow_Cards_Per_Match=('ycards', 'mean'),
    Avg_Red_Cards_Per_Match=('rcards', 'mean'),
).reset_index()
save(ref, 'avg_foulsCards_given_per_referee.csv', sort_by='Matches_Officiated',
     round_cols=['Avg_Fouls_Per_Match', 'Avg_Yellow_Cards_Per_Match', 'Avg_Red_Cards_Per_Match'])

# 5. Shot accuracy rate
home_sa = df.groupby('HomeTeam').agg(total_shots=('HS', 'sum'), total_sot=('HST', 'sum')).reset_index().rename(columns={'HomeTeam': 'team'})
away_sa = df.groupby('AwayTeam').agg(total_shots=('AS', 'sum'), total_sot=('AST', 'sum')).reset_index().rename(columns={'AwayTeam': 'team'})
sa = pd.concat([home_sa, away_sa]).groupby('team').sum().reset_index()
sa['shot_accuracy_rate_percentage'] = (sa['total_sot'] * 100.0 / sa['total_shots']).round(2)
save(sa, 'shot_accuracy_rate_percentage.csv', sort_by='shot_accuracy_rate_percentage')

# 6. Referees with highest avg cards per game
ref['Avg_Cards'] = (ref['Total_Yellow_Cards'] + ref['Total_Red_Cards']) / ref['Matches_Officiated']
save(ref[['Referee', 'Matches_Officiated', 'Avg_Cards']], 'referee_highest_avg_card_per_game.csv',
     sort_by='Avg_Cards', round_cols=['Avg_Cards'])

# 7. Goals per match by date
gpd = df.assign(total_goals=df.FTHG + df.FTAG).groupby('Date').agg(
    matches_played=('total_goals', 'count'), total_goals=('total_goals', 'sum')
).reset_index()
gpd['goals_per_match'] = (gpd['total_goals'] / gpd['matches_played']).round(2)
save(gpd, 'goals_per_match_overSeason_byDate.csv', sort_by='goals_per_match')

# 8. Cards per match by date
cpd = df.assign(total_cards=df.HC + df.AC + df.HR + df.AR).groupby('Date').agg(
    matches_played=('total_cards', 'count'), total_cards=('total_cards', 'sum')
).reset_index()
cpd['cards_per_match'] = (cpd['total_cards'] / cpd['matches_played']).round(2)
save(cpd, 'cards_per_match_overSeason_byDate.csv', sort_by='cards_per_match')
# NOTE: mirrors the original query's own use of HC+AC (corners) + red cards under the
# "cards_per_match" label -- kept as-is for fidelity to the source project (see writeup).

# 9. Referee performance by month
rpm = df.assign(fouls=df.HF + df.AF, cards=df.HC + df.AC + df.HR + df.AR).groupby(['Month', 'Referee']).agg(
    matches_played=('fouls', 'count'), total_fouls=('fouls', 'sum'), total_cards=('cards', 'sum')
).reset_index()
rpm['fouls_per_match'] = (rpm['total_fouls'] / rpm['matches_played']).round(2)
rpm['cards_per_match'] = (rpm['total_cards'] / rpm['matches_played']).round(2)
rpm = rpm.rename(columns={'Month': 'month'})
save(rpm, 'Referee_performance_by_month.csv', sort_by=['month', 'Referee'], ascending=True)

# 10. Top shooting teams
home_s = df.groupby('HomeTeam')['HS'].sum().rename('total_shots')
away_s = df.groupby('AwayTeam')['AS'].sum().rename('total_shots')
shots = (home_s.add(away_s, fill_value=0)).reset_index().rename(columns={'index': 'team'})
shots.columns = ['team', 'total_shots']
save(shots, 'top_shoting_teams(mostShotsTaken).csv', sort_by='total_shots')

# 11. Highest scoring matches (top 5)
top5 = df.assign(total_goals=df.FTHG + df.FTAG).sort_values(['total_goals', 'Date'], ascending=[False, True]).head(5)
save(top5[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'total_goals']], 'top5highestScoringMatches.csv')

# 12. Most fouls committed per team
home_f = df.groupby('HomeTeam')['HF'].sum()
away_f = df.groupby('AwayTeam')['AF'].sum()
fouls_t = (home_f.add(away_f, fill_value=0)).reset_index()
fouls_t.columns = ['team', 'total_fouls']
save(fouls_t, 'most_fouls_committed_per_team.csv', sort_by='total_fouls')

# 13. Teams with most cards (yellow + red)
home_c = df.groupby('HomeTeam').apply(lambda g: (g.HY + g.HR).sum(), include_groups=False)
away_c = df.groupby('AwayTeam').apply(lambda g: (g.AY + g.AR).sum(), include_groups=False)
cards_t = (home_c.add(away_c, fill_value=0)).reset_index()
cards_t.columns = ['team', 'total_cards']
save(cards_t, 'most_cards_per_team.csv', sort_by='total_cards')

# 14. Fouls-to-card ratio per team
fc = fouls_t.merge(cards_t, on='team')
fc['fouls_to_card_ratio'] = (fc['total_fouls'] / fc['total_cards']).round(2)
save(fc, 'fouls_to_card_ratio_perTeam.csv', sort_by='fouls_to_card_ratio')

# 15. Comebacks: trailing at HT, winning (or reverse) at FT
comebacks = df[((df.HTHG < df.HTAG) & (df.FTHG > df.FTAG)) | ((df.HTHG > df.HTAG) & (df.FTHG < df.FTAG))]
save(comebacks[['Date', 'HomeTeam', 'AwayTeam', 'HTHG', 'HTAG', 'FTHG', 'FTAG']], 'comebacks_teamLosing_atHalftime_winningFulltime.csv', sort_by='Date', ascending=True)

# 16. Home clean sheets vs away clean sheets
home_cs = df.assign(home_cs=(df.FTAG == 0).astype(int)).groupby('HomeTeam')['home_cs'].sum()
away_cs = df.assign(away_cs=(df.FTHG == 0).astype(int)).groupby('AwayTeam')['away_cs'].sum()
cs_ha = pd.concat([home_cs, away_cs], axis=1).fillna(0).astype(int).reset_index().rename(columns={'index': 'team'})
save(cs_ha, 'home_clean_sheetVSaway_clean_sheet.csv', sort_by='team', ascending=True)

# 17. Total clean sheets per team
cs_ha['total_clean_sheet'] = cs_ha['home_cs'] + cs_ha['away_cs']
save(cs_ha[['team', 'total_clean_sheet']], 'total_clean_sheets_per_team.csv', sort_by='total_clean_sheet')

# 18. Shots faced per team (shots conceded)
home_sf = df.groupby('HomeTeam')['AS'].sum()  # home team faces the away team's shots
away_sf = df.groupby('AwayTeam')['HS'].sum()  # away team faces the home team's shots
sf = (home_sf.add(away_sf, fill_value=0)).reset_index()
sf.columns = ['team', 'total_shots_faced']
save(sf, 'total_shots_faced_per_team.csv', sort_by='total_shots_faced')

# 19. Goals scored home vs away per team
gh = df.groupby('HomeTeam')['FTHG'].sum().rename('goals_at_home')
ga_ = df.groupby('AwayTeam')['FTAG'].sum().rename('goals_at_away')
gs = pd.concat([gh, ga_], axis=1).fillna(0).astype(int).reset_index().rename(columns={'index': 'team'})
save(gs, 'goals_scored_homeVSaway_perTeam.csv', sort_by='team', ascending=True)

# 20. Total goals scored per team
gs['total_goal_scored'] = gs['goals_at_home'] + gs['goals_at_away']
save(gs[['team', 'total_goal_scored']], 'total_goal_scored_perTeam.csv', sort_by='total_goal_scored')

# 21. Avg goals scored/conceded per team
home_avg = df[['HomeTeam', 'FTHG', 'FTAG']].rename(columns={'HomeTeam': 'team', 'FTHG': 'scored', 'FTAG': 'conceded'})
away_avg = df[['AwayTeam', 'FTAG', 'FTHG']].rename(columns={'AwayTeam': 'team', 'FTAG': 'scored', 'FTHG': 'conceded'})
avg_gc = pd.concat([home_avg, away_avg]).groupby('team').agg(avg_goal_scored=('scored', 'mean'), avg_goal_conceded=('conceded', 'mean')).reset_index()
save(avg_gc, 'avg_goal_scoredConceded_perTeam.csv', sort_by='avg_goal_scored', round_cols=['avg_goal_scored', 'avg_goal_conceded'])

# 22. Biggest win margins (top 5)
margins = df.assign(goal_difference=(df.FTHG - df.FTAG).abs()).sort_values('goal_difference', ascending=False).head(5)
save(margins[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'goal_difference']], 'biggest_win_margins(largestGoalDifference).csv')

# 23. Points table
hp = df.assign(
    points=np.select([df.FTHG > df.FTAG, df.FTHG == df.FTAG], [3, 1], default=0),
    wins=(df.FTHG > df.FTAG).astype(int), draws=(df.FTHG == df.FTAG).astype(int), losses=(df.FTHG < df.FTAG).astype(int)
)[['HomeTeam', 'points', 'wins', 'draws', 'losses']].rename(columns={'HomeTeam': 'team'})
ap = df.assign(
    points=np.select([df.FTAG > df.FTHG, df.FTAG == df.FTHG], [3, 1], default=0),
    wins=(df.FTAG > df.FTHG).astype(int), draws=(df.FTAG == df.FTHG).astype(int), losses=(df.FTAG < df.FTHG).astype(int)
)[['AwayTeam', 'points', 'wins', 'draws', 'losses']].rename(columns={'AwayTeam': 'team'})
pts = pd.concat([hp, ap]).groupby('team').sum().reset_index()
save(pts, 'team_points_wins_draws_losses.csv', sort_by='points')

# 24. First-half vs second-half scoring patterns
fh_sh = pd.DataFrame([{
    'avg_halftime_goals': round((df.HTHG + df.HTAG).mean(), 2),
    'avg_secondhalf_goals': round(((df.FTHG - df.HTHG) + (df.FTAG - df.HTAG)).mean(), 2),
}])
save(fh_sh, 'firtsHalf-vs-secondHalf_scoring_patterns.csv')

# 25. Home advantage: avg points home vs away
hpt = df.assign(hpts=np.select([df.FTHG > df.FTAG, df.FTHG == df.FTAG], [3, 1], default=0))[['HomeTeam', 'hpts']].rename(columns={'HomeTeam': 'team'})
apt = df.assign(apts=np.select([df.FTAG > df.FTHG, df.FTAG == df.FTHG], [3, 1], default=0))[['AwayTeam', 'apts']].rename(columns={'AwayTeam': 'team'})
home_avg_pts = hpt.groupby('team')['hpts'].mean().rename('avg_home_points')
away_avg_pts = apt.groupby('team')['apts'].mean().rename('avg_away_points')
avgpts = pd.concat([home_avg_pts, away_avg_pts], axis=1).reset_index().rename(columns={'index': 'team'})
save(avgpts, 'avgPoints_atHome-vs-atAway.csv', sort_by='team', ascending=True, round_cols=['avg_home_points', 'avg_away_points'])

# 26. BONUS: games where the half-time result changed by full time (HTR != FTR)
changed = int((df['HTR'] != df['FTR']).sum())
save(pd.DataFrame([{'games_changed_result': changed}]), 'resultChangedFromHalfTimeToFullTime.csv')

# 27. BONUS: full discipline profile per team (fouls + cards + per-match rates)
home_d = df.assign(f=df.HF, y=df.HY, r=df.HR)[['HomeTeam', 'f', 'y', 'r']].rename(columns={'HomeTeam': 'Team'})
away_d = df.assign(f=df.AF, y=df.AY, r=df.AR)[['AwayTeam', 'f', 'y', 'r']].rename(columns={'AwayTeam': 'Team'})
disc = pd.concat([home_d, away_d]).groupby('Team').agg(
    total_fouls=('f', 'sum'), total_yellow_cards=('y', 'sum'), total_red_cards=('r', 'sum'),
    avg_fouls_per_match=('f', 'mean'), avg_yellow_cards_per_match=('y', 'mean'), avg_red_cards_per_match=('r', 'mean'),
).reset_index()
save(disc, 'total_yellowRedCards_fouls_perTeam.csv', sort_by='total_fouls',
     round_cols=['avg_fouls_per_match', 'avg_yellow_cards_per_match', 'avg_red_cards_per_match'])

print("\nDone. 27 CSVs written to ./csv/")
