# EPL 2025-26 Season Analysis — Rebuilt From Scratch

This is the same project as the original **EPL 2024-25 Data Analysis** repo, rebuilt end‑to‑end
for the **2025-26** season. Everything below is organized as the five steps you asked for:
**find data → clean it → analyze it → visualize it → comment on it.** Every file this guide
references is included in this package and already contains real results computed from the
actual, completed 2025-26 season (380 matches, 15 Aug 2025 → 24 May 2026).

---

## 1. Where to find the data

The original project's `season-2425.csv` uses a very specific, well-known schema (`Date,
HomeTeam, AwayTeam, FTHG, FTAG, FTR, HTHG, HTAG, HTR, Referee, HS, AS, HST, AST, HF, AF, HC, AC,
HY, AY, HR, AR`). That's the standard **football-data.co.uk** match-stats format. Two ways to get
next season's file in that exact shape:

**Option A — the cleaned mirror (what I used, and what matches the repo's format exactly):**
DataHub republishes the same data with no betting-odds columns, one file per season:
- Season index: `https://datahub.io/football/english-premier-league`
- Direct 2025-26 file: **`https://datahub.io/football/english-premier-league/_r/-/season-2526.csv`**
- Naming pattern for any other season: `season-<YY><YY>.csv` (e.g. `season-2627.csv` next year)

**Option B — the primary source (more columns, incl. betting odds):**
- `https://www.football-data.co.uk/englandm.php` → Premier League → season CSV
- File path pattern: `mmz4281/<season code>/E0.csv` (e.g. `mmz4281/2526/E0.csv`)
- Use this one if you later want to extend the "Future Enhancements" ideas from the original
  README (e.g. market-implied probabilities), since it carries odds columns A doesn't.

**Backups if either site is ever down:** search Kaggle for "English Premier League 2025-26" —
several mirrors of the same football-data.co.uk source exist there (e.g.
`mertbayraktar/english-premier-league-2526-season`).

I already downloaded and verified Option A for you — see `dataset/premier-league/season-2526.csv`.

### Column reference (same for every season)
| Column | Meaning | Column | Meaning |
|---|---|---|---|
| Date | Match date | HF / AF | Home/Away fouls conceded |
| HomeTeam / AwayTeam | Team names | HC / AC | Home/Away corners |
| FTHG / FTAG | Full-time goals | HY / AY | Home/Away yellow cards |
| FTR | Full-time result (H/D/A) | HR / AR | Home/Away red cards |
| HTHG / HTAG / HTR | Half-time goals & result | HS / AS | Home/Away total shots |
| Referee | Match official | HST / AST | Home/Away shots on target |

---

## 2. How I cleaned it

The football-data.co.uk format is already tidy — that's why it's a popular teaching dataset — but
I still ran the checks you'd want to run on any "new" data before trusting it:

1. **Completeness**: 380 rows (20 teams × 38 games), every team appears exactly 38 times, no
   duplicate fixtures, date range runs the full season through the final matchday (24 May 2026,
   when all 10 remaining matches kick off simultaneously — that's the tell that the season is over,
   not "in progress").
2. **Missing values**: zero nulls across all 22 columns, including `Referee`.
3. **Squad changes**: 2025-26 has three different clubs than 2024-25. **Leeds United, Burnley, and
   Sunderland** were promoted and replace **Ipswich, Leicester, and Southampton**, who were
   relegated. If you're ever comparing season-over-season, don't assume the 20 team names are
   identical — check `set(df.HomeTeam.unique())` for both seasons first.
4. **The one real gotcha — a reserved SQL keyword**: the away-shots column is literally named
   `AS` in the CSV. `AS` is a reserved word in SQL (used for aliasing), so if you import this file
   into MySQL as-is, every query that references that column will either fail to parse or silently
   alias something else. **Rename it on import** — I used `AwayShots` (matching the original
   project's own convention, visible in its queries) — or wrap every reference in backticks
   (`` `AS` ``) if you'd rather keep the original name.
5. **Types**: `Date` needs parsing as a date (not string) if you want to `GROUP BY` month or sort
   chronologically; everything else is already numeric.

---

## 3. How I analyzed it

The original project analyzed data two ways — SQL for the full query set, Python/pandas +
`scipy` for statistical testing. I rebuilt both.

### 3a. SQL (MySQL)
`EPL Queries 2025-26.sql` is a straight port of the original `EPL Queries.sql` — same 25 queries,
plus 2 more that the original repo's `csv/` folder clearly contained but its `.sql` file didn't
(a half-time→full-time result-change count, and a per-team discipline profile), so this version is
fully self-contained at 27 queries. To use it:
1. Create a schema: `CREATE DATABASE epl_stats;`
2. Import `dataset/premier-league/season-2526.csv` as a table named `season2526` (Table Data
   Import Wizard in MySQL Workbench is the easiest route), renaming the `AS` column per §2.4.
3. Run the file top to bottom, or query-by-query if you want to export each result set yourself.

It covers four groups of analysis, same as the original:
- **Team performance** — conversion rate, shot accuracy, points table, home/away splits, clean sheets
- **Match analysis** — highest-scoring games, biggest margins, comebacks, half↔full-time swings
- **Referee & discipline** — fouls/cards per referee, monthly trends, fouls-to-card ratio
- **Season-wide stats** — total goals/cards, per-match averages, first-half vs second-half scoring

### 3b. Python / statistical testing
`EPL_2025_26_Data_Analysis.ipynb` mirrors the original notebook's structure exactly (same 6
cells: import libraries → upload data → run the statistical-analysis cell), pointed at
`season-2526.csv` instead of `season-2425.csv`. I ran it against the real data so you can see what
it produces before you touch it. It computes a league table from scratch, aggregates clean sheets
and cards per team, then runs three tests:

| Test | Result | Interpretation |
|---|---|---|
| Pearson r: Clean sheets vs. league position | **r = ‑0.690, p = 0.0008** | Strong, statistically significant. Fewer clean sheets → worse (higher-numbered) position, reliably. |
| Pearson r: Total cards vs. league position | **r = 0.291, p = 0.213** | Weak, **not** significant (p > 0.05). This season, card counts don't reliably predict where a team finished. |
| Paired t-test: home goals vs. away goals | **t = 3.642, p = 0.0003** | Highly significant. Home advantage is real: 1.53 goals/game at home vs. 1.22 away. |

If you don't have MySQL handy, `run_analysis.py` is a bonus script I wrote that reproduces every
one of the 27 SQL queries in pure pandas and writes them straight to `csv/` — useful for checking
your SQL results match, or as your whole analysis layer if you'd rather skip MySQL entirely.

---

## 4. How to visualize it (Power BI)

I opened the original project's `.pbix` file to see exactly how it was built — it's 10 report
pages built from the same query outputs your `csv/` folder now has (mine's included as
`excel/EPL_2025_26_All_Analyses.xlsx`, all 27 tables as one workbook, if you'd rather import a
single file into Power BI instead of 27 separate CSVs).

I can't generate a working `.pbix` from here — that file format is a compressed, Power-BI-Desktop-
specific data model (not something a script can safely hand-assemble), so it has to be built in
the actual app. But I mapped out precisely what the original built, page by page, so you can
recreate it fast. **See `POWERBI_REBUILD_GUIDE.md`** for the full page-by-page spec (which chart
type, which fields, which CSV, on every one of the 10 pages).

General workflow either way:
1. Power BI Desktop → **Get Data → Text/CSV** → import everything in `csv/` (or the one xlsx).
2. Since these are pre-aggregated, mostly single-table results (not one big fact table), you won't
   need many relationships — most pages pull from exactly one query result.
3. Build pages in the order in the guide; it goes overview → team performance → referees →
   efficiency rates → shots/clean sheets/discipline, same arc as the original.

---

## 5. How to comment on it

A good insight in this kind of write-up has three parts: **the number → what it's compared
against → why it matters.** Here's that pattern applied to five real findings from this season's
data, as a model for writing your own:

- **Arsenal won the title with 85 points**, seven clear of second-placed Man City (78) — the
  biggest final-day-locked gap at the top since [whichever season you're benchmarking against];
  worth checking against 2024-25's 84-point winning total (Liverpool) to say whether the league
  got more or less competitive at the top.
- **Home advantage is statistically real, not just folklore**: teams averaged 1.53 goals at home
  vs. 1.22 away (t = 3.64, p < 0.001). That's worth pairing with the `avgPoints_atHome-vs-atAway.csv`
  breakdown to see which specific teams over- or under-perform that league-wide pattern.
- **Defense predicts final position far better than discipline does**: clean sheets correlate
  strongly with league position (r = ‑0.69, p < 0.001), but yellow/red cards don't (r = 0.29,
  p = 0.21). That's a useful, slightly counter-intuitive line — "getting booked a lot didn't cost
  teams points this season" is a more interesting claim than the generic "discipline matters."
- **Brentford were the league's most clinical team**, leading both goal conversion (13.6%) and
  shot accuracy (36.3%) — despite finishing mid-table (9th, 53 pts). That gap between underlying
  efficiency and final position is exactly the kind of "moneyball" observation that makes a stats
  write-up more interesting than the league table alone.
- **145 of 380 matches (38%) had their half-time result overturned or drawn level by full time**,
  and 23 of those were full reversals (losing at the break, winning at the end) — a concrete way
  to quantify "this league is full of second-half drama" instead of just asserting it.

When you write your own comments, always check the p-value before treating a correlation as a
real pattern (anything above ~0.05 means treat it as noise, as with cards vs. position above), and
always give the reader something to compare a number against — a league average, last season, or
another team — since a number on its own ("Team X had 66 clean sheets") doesn't mean anything
without that context.

---

## Project structure

```
EPL-2025-26-Data-Analysis/
├── README.md                                    <- this file
├── POWERBI_REBUILD_GUIDE.md                     <- page-by-page Power BI rebuild spec
├── POWERBI_STEP_BY_STEP_GUIDE.md                <- full beginner build guide: Power Query M + DAX
├── EPL Queries 2025-26.sql                      <- 27 MySQL queries (season2526 table)
├── EPL_2025_26_Data_Analysis.ipynb              <- statistical analysis notebook (Colab or local)
├── run_analysis.py                              <- bonus: same 27 analyses in pure pandas, no MySQL needed
├── dashboard/EPL_2025-26_Dashboard.html         <- offline-capable interactive dashboard (double-click to open)
├── powerbi/EPL_2025-26_Dashboard.pbix           <- the manually-built Power BI file (add your own)
├── dataset/premier-league/
│   ├── season-2526.csv                          <- raw source data (380 matches, verified complete)
│   ├── team_locations.csv                       <- stadium coordinates, for the map visual
│   └── team_top_players.csv                     <- top scorer / assist provider per club
├── csv/                                         <- 27 query result CSVs (one per analysis)
└── excel/EPL_2025_26_All_Analyses.xlsx          <- all 27 results as one formatted workbook
```

### Two modeling gotchas worth documenting (found while building the manual version)

- **League table sort order:** if you rank teams with a DAX `RANKX` measure, sorting the visual by
  *Total Points* alone won't match the rank numbers on tied points — sort explicitly by the rank
  measure itself (ascending), or ties will display out of order even though the numbers themselves
  are correct.
- **Counts vs. ratios on the unpivoted team table:** any measure built on a "one row per team per
  match" table (760 rows for a 380-match season) double-counts anything that isn't team-specific —
  total draws, for instance, comes out as 208 instead of the real 104. Ratios built the same way
  (e.g. fouls-to-cards) are unaffected, since the doubling cancels out top and bottom. Match-level
  totals should always come from the original one-row-per-match table, not the unpivoted one.

## Next season (2026-27) and beyond

Since the source keeps a stable, predictable URL per season
(`season-<YY><YY>.csv`), rolling this whole project forward each year is mostly: swap the file,
re-run `run_analysis.py` (or the `.sql` file), re-point the Power BI file at the new CSVs, and
re-check §2.3 for squad changes. The original README's "Future Enhancements" section (adding
other leagues, xG, possession, a real predictive model) applies just as well here if you want to
extend this rather than just refresh it season to season.
