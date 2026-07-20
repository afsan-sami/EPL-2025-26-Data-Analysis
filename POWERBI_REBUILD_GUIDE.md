# Power BI Rebuild Guide

I opened the original project's `EPL stats with Power BI.pbix` directly (it's a zip archive
internally — `Report/Layout` holds the page/visual definitions as JSON) to see exactly what was
built, rather than guessing. It has **10 pages** and uses 3–4 chart types total, mostly built
straight off single query results — very little modeling needed. Titles below are copied from the
file where the original author set one; where a visual had no title set, I've named the most
likely source table for that page's theme and flagged it as inferred.

For every page: **Home ribbon → New Page**, then **Get Data → Text/CSV** (or open the one
`EPL_2025_26_All_Analyses.xlsx` and pick the matching sheet) for the file named, then drag fields
into the chart type named.

| Page | Chart type(s) | Title | Source file (2025-26 rebuild) |
|---|---|---|---|
| 1 | Table + Clustered column + Table + 3 Cards | *"Average Home Point vs Away Point"* (confirmed) | `avgPoints_atHome-vs-atAway.csv` for the chart; `team_points_wins_draws_losses.csv` for the league table; `totalMatches_goals_yellowRedCards_avgGoals_perMatch.csv` for the 3 KPI cards (total matches / total goals / avg goals per match) |
| 2 | 9 Cards + 2 textboxes + 1 column chart | *(overview/cover page)* | Same season-summary file as above, split across 9 cards (total matches, total goals, home goals, away goals, yellow cards, red cards, avg goals/match, avg home goals, avg away goals) |
| 3 | 2 Clustered column charts | *"General Team Performances – Home"* / *"– Away"* (confirmed) | `goals_scored_homeVSaway_perTeam.csv` — one chart filtered/using `goals_at_home`, the other `goals_at_away` |
| 4 | 2 Clustered bar + 1 Clustered column | *(inferred: discipline)* | `most_fouls_committed_per_team.csv` and `most_cards_per_team.csv` |
| 5 | 2 Clustered column + 1 Table | *"Number of the Matches for Referees"* / *"Total Fouls by Referee"* (confirmed) | `avg_foulsCards_given_per_referee.csv` — `Matches_Officiated` for one chart, `Total_Fouls` for the other; the same file as the table |
| 6 | 2 Clustered column + 1 Bar chart | *"Shot/Goal Rate (%)"* / *"Foul/Card Ratio (%)"* / *"Shot Accuracy Rate (%)"* (all confirmed) | `goalConversionRate_eachTeam.csv`, `fouls_to_card_ratio_perTeam.csv`, `shot_accuracy_rate_percentage.csv` respectively |
| 7 | Donut chart | *"Total Shots per Team"* (confirmed) | `top_shoting_teams(mostShotsTaken).csv` |
| 8 | 1 Column chart | *(inferred: goals scored)* | `total_goal_scored_perTeam.csv` |
| 9 | 2 Clustered column charts | *"Home Clean Sheets vs Away Clean Sheets by Team"* (confirmed) | `home_clean_sheetVSaway_clean_sheet.csv` |
| 10 | 2 Column charts | *"Total Fouls by Team"* (confirmed) | `most_fouls_committed_per_team.csv` (paired with `total_yellowRedCards_fouls_perTeam.csv` for the second chart) |

## Notes on rebuilding

- **Almost nothing needs a relationship.** Nearly every page pulls from exactly one flat query
  result, so you can load each CSV as its own independent table and build directly off it — this
  mirrors how the original was built (straight off 25+ separate SQL exports, not one big star
  schema).
- **Cards (Page 1 & 2)**: select a single numeric column from the season-summary table, drop it
  into a Card visual, and set the label manually (e.g. "Total Goals This Season").
- **Color/theme**: the original uses Power BI's built-in **Accessible Neutral** theme — pick that
  under View → Themes if you want a visually identical result, not just structurally identical.
- **The two "highlight" tables** (`top5highestScoringMatches.csv` and
  `biggest_win_margins(largestGoalDifference).csv`) don't appear on their own page in the original
  layout — they're better suited to a table/card tooltip or a "did you know" text box if you want
  to surface them at all, e.g. layered into Page 1 or 2 as extra cards.
- **Sort order matters more than it seems**: for anything ranked (conversion rate, shot accuracy,
  cards), sort the visual by the metric descending, not alphabetically by team — that's what makes
  a "top performers" chart actually readable at a glance.
