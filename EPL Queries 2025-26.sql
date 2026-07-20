-- ============================================================================
-- EPL 2025-26 Season Analysis — SQL Queries
-- Adapted from the EPL 2024-25 project, pointed at the season2526 table.
--
-- IMPORTANT IMPORT NOTE:
-- The raw CSV column for away shots is literally named "AS". AS is a reserved
-- SQL keyword (used for aliasing), so when importing season-2526.csv into
-- MySQL you must rename that column to something else, e.g. AwayShots.
-- Every query below assumes that rename has been done. If you'd rather keep
-- the column named AS, wrap every reference in backticks: `AS`.
-- ============================================================================

USE epl_stats;
SELECT *
FROM season2526;

-- Goal Conversion Rate
SELECT Team, SUM(total_goals) AS total_goals, SUM(total_shots) AS total_shots,
    ROUND(SUM(total_goals) * 100.0 / NULLIF(SUM(total_shots), 0), 2) AS conversion_rate_percentage
FROM (
    SELECT HomeTeam AS Team, SUM(FTHG) AS total_goals, SUM(HS) AS total_shots
    FROM season2526
    GROUP BY HomeTeam
    UNION ALL
    SELECT AwayTeam AS Team, SUM(FTAG) AS total_goals, SUM(AwayShots) AS total_shots
    FROM season2526
    GROUP BY AwayTeam
) AS combined
GROUP BY Team
ORDER BY conversion_rate_percentage DESC;

-- Win/Draw/Loss count for each team at home vs away.
SELECT Team, SUM(home_wins)  AS home_wins, SUM(home_draws) AS home_draws, SUM(home_losses) AS home_losses, SUM(away_wins)  AS away_wins,
    SUM(away_draws) AS away_draws, SUM(away_losses) AS away_losses
FROM (
    SELECT
        HomeTeam AS Team,
        CASE WHEN FTR = 'H' THEN 1 ELSE 0 END AS home_wins,
        CASE WHEN FTR = 'D' THEN 1 ELSE 0 END AS home_draws,
        CASE WHEN FTR = 'A' THEN 1 ELSE 0 END AS home_losses,
        0 AS away_wins,
        0 AS away_draws,
        0 AS away_losses
    FROM season2526
    UNION ALL
    SELECT
        AwayTeam AS Team,
        0 AS home_wins,
        0 AS home_draws,
        0 AS home_losses,
        CASE WHEN FTR = 'A' THEN 1 ELSE 0 END AS away_wins,
        CASE WHEN FTR = 'D' THEN 1 ELSE 0 END AS away_draws,
        CASE WHEN FTR = 'H' THEN 1 ELSE 0 END AS away_losses
    FROM season2526
) AS results
GROUP BY Team
ORDER BY Team;

-- Total matches, goals, home&away goals, yellow&red cards, avg home&away goals per match
SELECT COUNT(*) AS total_matches, SUM(FTHG) + SUM(FTAG) AS total_goals, SUM(FTHG) AS total_home_goals, SUM(FTAG) AS total_away_goals,
    SUM(HY) + SUM(AY) AS total_yellow_cards, SUM(HR) + SUM(AR) AS total_red_cards, ROUND((SUM(FTHG) + SUM(FTAG)) * 1.0 / COUNT(*), 2) AS avg_goals_per_match,
    ROUND(SUM(FTHG) * 1.0 / COUNT(*), 2) AS avg_home_goals_per_match, ROUND(SUM(FTAG) * 1.0 / COUNT(*), 2) AS avg_away_goals_per_match
FROM season2526;

-- Average fouls/cards given per referee
SELECT Referee, COUNT(*) AS Matches_Officiated, SUM(HF + AF) AS Total_Fouls, SUM(HY + AY) AS Total_Yellow_Cards,
    SUM(HR + AR) AS Total_Red_Cards, ROUND(AVG(HF + AF), 2) AS Avg_Fouls_Per_Match, ROUND(AVG(HY + AY), 2) AS Avg_Yellow_Cards_Per_Match,
    ROUND(AVG(HR + AR), 2) AS Avg_Red_Cards_Per_Match
FROM season2526
WHERE Referee IS NOT NULL
GROUP BY Referee;

-- Shot accuracy – Shots on target ÷ total shots.
SELECT Team, SUM(total_shots) AS total_shots, SUM(total_shots_on_target) AS total_shots_on_target,
    ROUND(SUM(total_shots_on_target) * 100.0 / NULLIF(SUM(total_shots), 0), 2) AS shot_accuracy_rate_percentage
FROM (
    SELECT HomeTeam AS Team, SUM(HS) AS total_shots, SUM(HST) AS total_shots_on_target
    FROM season2526
    GROUP BY HomeTeam
    UNION ALL
    SELECT AwayTeam AS Team, SUM(AwayShots) AS total_shots, SUM(AST) AS total_shots_on_target
    FROM season2526
    GROUP BY AwayTeam
) AS combined
GROUP BY Team
ORDER BY shot_accuracy_rate_percentage DESC;

-- Referees with highest average cards per game.
SELECT Referee, COUNT(*) AS Matches_Officiated, AVG(HY + AY + HR + AR) AS Avg_Cards
FROM season2526
WHERE Referee IS NOT NULL
GROUP BY Referee
ORDER BY Avg_Cards DESC;

-- Goals per match over the season – by date.
SELECT
    Date,
    COUNT(*) AS matches_played,
    SUM(FTHG + FTAG) AS total_goals,
    ROUND(SUM(FTHG + FTAG) * 1.0 / COUNT(*), 2) AS goals_per_match
FROM season2526
GROUP BY Date
ORDER BY goals_per_match DESC;

-- Cards per match over the season – by date.
SELECT
	Date,
    COUNT(*) AS matches_played,
    SUM(HC + AC + HR + AR) AS total_cards,
    ROUND(SUM(HC + AC + HR + AR) * 1.0 / COUNT(*), 2) AS cards_per_match
FROM season2526
GROUP BY Date
ORDER BY cards_per_match DESC;

-- Referee performance by month – Do card counts vary over time?
SELECT
    EXTRACT(MONTH FROM Date) AS month,
    Referee,
    COUNT(*) AS matches_played,
	SUM(HF + AF) AS total_fouls,
    SUM(HC + AC + HR + AR) AS total_cards,
	ROUND(SUM(HF + AF) * 1.0 / NULLIF(COUNT(*), 0), 2) AS fouls_per_match,
    ROUND(SUM(HC + AC + HR + AR) * 1.0 / NULLIF(COUNT(*), 0), 2) AS cards_per_match
FROM season2526
GROUP BY Referee, EXTRACT(MONTH FROM Date);

-- Top shooting teams – Most shots taken (HS + AS).
SELECT team, SUM(total_shots) AS total_shots
FROM(
	SELECT HomeTeam AS team, SUM(HS) AS total_shots
    FROM season2526
    GROUP BY HomeTeam
    UNION ALL
    SELECT AwayTeam AS team, SUM(AwayShots) AS total_shots
    FROM season2526
    GROUP BY AwayTeam
) AS shots
GROUP BY team
ORDER BY team ASC;

-- Highest scoring matches – List matches ordered by total goals (FTHG + FTAG) descending.
SELECT Date, HomeTeam, AwayTeam, FTHG, FTAG, (FTHG + FTAG) AS total_goals
FROM season2526
ORDER BY total_goals DESC, Date ASC
LIMIT 5;

-- Most fouls committed per team (HF + AF).
SELECT team, SUM(total_fouls) AS total_fouls
FROM(
	SELECT HomeTeam AS team, SUM(HF) AS total_fouls
    FROM season2526
    GROUP BY HomeTeam
    UNION ALL
    SELECT AwayTeam AS team, SUM(AF) AS total_fouls
    FROM season2526
    GROUP BY AwayTeam
) AS fouls
GROUP BY team
ORDER BY team ASC;

-- Teams with most cards – Yellow and red combined.
SELECT team, SUM(total_cards) AS total_cards
FROM(
	SELECT HomeTeam AS team, SUM(HY + HR) AS total_cards
    FROM season2526
    GROUP BY HomeTeam
    UNION ALL
    SELECT AwayTeam AS team, SUM(AY + AR) AS total_cards
    FROM season2526
    GROUP BY AwayTeam
) AS cards
GROUP BY team
ORDER BY team ASC;

-- Fouls-to-card ratio per team – Fouls ÷ Cards.
SELECT team, SUM(total_fouls) AS total_fouls, SUM(total_cards) AS total_cards, ROUND(SUM(total_fouls) * 1.0 / NULLIF(SUM(total_cards), 0), 2) AS fouls_to_card_ratio
FROM(
	SELECT HomeTeam AS team, HF AS total_fouls, (HY + HR) AS total_cards
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, AF AS total_fouls, (AY + AR) AS total_cards
    FROM season2526
) AS all_stats
GROUP BY team
ORDER BY fouls_to_card_ratio DESC;

-- Comebacks – Team losing at halftime but winning at full time.
SELECT Date, HomeTeam, AwayTeam, HTHG, HTAG, FTHG, FTAG
FROM season2526
WHERE (HTHG < HTAG AND FTHG > FTAG) OR (HTHG > HTAG AND FTHG < FTAG);

-- Home clean sheets vs away clean sheets.
SELECT team, SUM(home_cs) AS home_clean_sheet, SUM(away_cs) AS away_clean_sheet
FROM (
	SELECT HomeTeam AS team,
    CASE WHEN FTAG = 0 THEN 1 ELSE 0 END AS home_cs, 0 AS away_cs
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, 0 AS home_cs, CASE WHEN FTHG = 0 THEN 1 ELSE 0 END AS away_cs
    FROM season2526
) AS cs
GROUP BY team
ORDER BY team;

-- Clean sheets count per team – How many matches each team kept a clean sheet.
SELECT team, SUM(clean_sheets) AS total_clean_sheet
FROM (
	SELECT HomeTeam AS team,
    CASE WHEN FTAG = 0 THEN 1 ELSE 0 END AS clean_sheets
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, CASE WHEN FTHG = 0 THEN 1 ELSE 0 END AS clean_sheets
    FROM season2526
) AS tcs
GROUP BY team
ORDER BY total_clean_sheet DESC;

-- Teams with most shots faced – Shots conceded as home + away.
SELECT team, SUM(shots_faced) AS total_shots_faced
FROM(
	SELECT HomeTeam AS team, AwayShots AS shots_faced
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, HS AS shots_faced
    FROM season2526
) AS sf
GROUP BY team
ORDER BY total_shots_faced DESC;

-- Goals scored at home vs away for each team.
SELECT team, SUM(home_goals) AS goals_at_home, SUM(away_goals) AS goals_at_away
FROM (
	SELECT HomeTeam AS team, FTHG AS home_goals, 0 AS away_goals
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, 0 AS home_goals, FTAG AS away_goals
    FROM season2526
) AS gs
GROUP BY team;

-- Teams with most goal scored – home + away.
SELECT team, SUM(total_goals) AS total_goal_scored
FROM(
	SELECT HomeTeam AS team, FTHG AS total_goals
    FROM season2526
    GROUP BY HomeTeam
    UNION ALL
    SELECT AwayTeam AS team, FTAG AS total_goals
    FROM season2526
    GROUP BY AwayTeam
) AS tg
GROUP BY team
ORDER BY total_goal_scored DESC;

-- Average goals scored/conceded per team (home + away combined).
SELECT team, ROUND(AVG(goal_scored), 2) AS avg_goal_scored, ROUND(AVG(goal_conceded), 2) AS avg_goal_conceded
FROM(
	SELECT HomeTeam AS team, FTHG AS goal_scored, FTAG AS goal_conceded
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, FTAG AS goal_scored, FTHG AS goal_conceded
    FROM season2526
) AS gsa
GROUP BY team;

-- Biggest win margins – Matches with the largest goal difference.
SELECT Date, HomeTeam, AwayTeam, FTHG, FTAG, ABS(FTHG - FTAG)  AS goal_difference
FROM season2526
ORDER BY goal_difference DESC
LIMIT 5;

-- Points table – Wins = 3 pts, Draws = 1 pt, Loss = 0 pts.
SELECT team, SUM(points) AS points, SUM(wins) AS wins, SUM(draws) AS draws, SUM(losses) AS losses
FROM (
	SELECT HomeTeam AS team, CASE WHEN FTHG > FTAG THEN 3 WHEN FTHG = FTAG THEN 1 ELSE 0 END AS points,
							 CASE WHEN FTHG > FTAG THEN 1 ELSE 0 END AS wins,
                             CASE WHEN FTHG = FTAG THEN 1 ELSE 0 END AS draws,
                             CASE WHEN FTHG < FTAG THEN 1 ELSE 0 END AS losses
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS team, CASE WHEN FTAG > FTHG THEN 3 WHEN FTAG = FTHG THEN 1 ELSE 0 END AS points,
							 CASE WHEN FTAG > FTHG THEN 1 ELSE 0 END AS wins,
                             CASE WHEN FTAG = FTHG THEN 1 ELSE 0 END AS draws,
                             CASE WHEN FTAG < FTHG THEN 1 ELSE 0 END AS losses
    FROM season2526
) AS pnt
GROUP BY team;

-- First-half vs second-half scoring patterns.
SELECT ROUND(AVG(HTHG + HTAG), 2) AS avg_halftime_goals, ROUND(AVG((FTHG - HTHG) + (FTAG - HTAG)), 2) AS avg_secondhalf_goals
FROM season2526;

-- Home advantage – Compare average points at home vs away.
SELECT team, ROUND(AVG(home_points), 2) AS avg_home_points, ROUND(AVG(away_points), 2) AS avg_away_points
FROM (
    SELECT HomeTeam AS Team,
           CASE WHEN FTHG > FTAG THEN 3 WHEN FTHG = FTAG THEN 1 ELSE 0 END AS home_points,
           NULL AS away_points
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS Team,
           NULL AS home_points,
           CASE WHEN FTAG > FTHG THEN 3 WHEN FTAG = FTHG THEN 1 ELSE 0 END AS away_points
    FROM season2526
) AS t
GROUP BY Team;

-- ============================================================================
-- Two extra queries (present as CSV/Excel outputs in the original repo but not
-- in its .sql file — added here so this file is fully self-contained).
-- ============================================================================

-- Games where the half-time result did NOT match the full-time result.
SELECT COUNT(*) AS games_changed_result
FROM season2526
WHERE HTR <> FTR;

-- Full discipline profile per team: fouls + cards, totals and per-match rates.
SELECT Team, SUM(total_fouls) AS total_fouls, SUM(total_yellow) AS total_yellow_cards, SUM(total_red) AS total_red_cards,
    ROUND(AVG(total_fouls), 2) AS avg_fouls_per_match, ROUND(AVG(total_yellow), 2) AS avg_yellow_cards_per_match,
    ROUND(AVG(total_red), 2) AS avg_red_cards_per_match
FROM (
    SELECT HomeTeam AS Team, HF AS total_fouls, HY AS total_yellow, HR AS total_red
    FROM season2526
    UNION ALL
    SELECT AwayTeam AS Team, AF AS total_fouls, AY AS total_yellow, AR AS total_red
    FROM season2526
) AS discipline
GROUP BY Team
ORDER BY total_fouls DESC;
