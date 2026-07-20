# Power BI — Full Build Guide (Load → Transform → Model → Visualize → Style)

Written for a first-time Power BI user, using `season-2526.csv` (from the earlier package).
Every formula below was tested against the real 2025-26 data before being written down here —
none of this is guessed syntax.

**Time estimate:** ~2-3 hours the first time through. The only step with real "code" is §2B; everything
else is clicking.

---

## 0. Before you start

1. Power BI Desktop is **Windows-only**, free, via the Microsoft Store or `powerbi.microsoft.com`. On
   Mac, you need Parallels/Bootcamp/a Windows VM — there's no native Mac version.
2. Have `season-2526.csv` saved somewhere you can find it.
3. Orient yourself to the interface: three icons on the far-left rail switch between **Report view**
   (build pages), **Data view** (inspect loaded tables), and **Model view** (see relationships). On the
   right: **Filters**, **Visualizations**, and **Fields** panes. The ribbon along the top has **Home**,
   **Insert**, **View**, etc.

---

## 1. Load the data

1. **Home → Get Data → Text/CSV**.
2. Browse to `season-2526.csv`. A preview window pops up.
3. Click **Transform Data** — not "Load". This opens the **Power Query Editor**, where all cleaning
   happens *before* the data ever reaches your report. (If you clicked Load by mistake, Home → Transform
   Data gets you back here.)
4. In the **Queries** pane on the left, rename the query from `season-2526` to **`season2526`** (no
   hyphen) — right-click the query name → **Rename**. DAX handles hyphenated table names, but it's more
   typing (`'season-2526'[FTHG]` vs. `season2526[FTHG]`), so drop it now.

---

## 2. Transform in Power Query

### 2A. Clean the main table (`season2526`) — all clicks, no code

1. **Check data types.** Look at the small icon at the left of each column header. `Date` should already
   show a calendar icon (Date type) since the file uses `YYYY-MM-DD`. All the stat columns (`FTHG`, `HS`,
   `HY`, etc.) should show `1.2` (whole number). If any show `ABC` (text) by mistake, click the icon →
   pick the correct type.
2. **Rename `AS` → `AwayShots`.** Right-click the `AS` column header → **Rename**. (Unlike MySQL, Power
   BI doesn't actually break on a column called `AS` — DAX always references columns as `Table[Column]`,
   so there's no keyword collision. Rename it anyway: scanning a Fields list for "AS" next to "AF", "AC",
   "AY" is genuinely confusing, and every formula below assumes this rename.)
3. **Add a Month column** (used later for the referee-by-month view). **Add Column → Custom Column**:
   - Name: `Month`
   - Formula: `= Date.Month([Date])`
4. **Home → Close & Apply.** This loads `season2526` (380 rows) into your model.

### 2B. Build the team-perspective table — the one step with real code

Here's the problem this solves: `season2526` has one row per **match**, with `HomeTeam` and `AwayTeam` as
separate columns. That's fine for match-level stats, but useless for "which team has the best conversion
rate" — you can't easily group by "team" when each team's data is split across two differently-named
columns depending on venue. The fix is to build a second table with **one row per team per match** (760
rows: 380 matches × 2 teams), which is the standard way to model this kind of data in Power BI.

1. In the Power Query Editor, right-click **`season2526`** in the Queries pane → **Reference**. This
   creates a new query that starts from your cleaned table.
2. Rename this new query to **`TeamMatches`**.
3. With `TeamMatches` selected, go to **View → Advanced Editor**. Delete everything in the box and paste
   this in its place:

```m
let
    Source = season2526,

    HomePerspective = Table.RenameColumns(
        Table.SelectColumns(Source, {"Date","HomeTeam","AwayTeam","FTHG","FTAG","HTHG","HTAG",
            "Referee","HS","AwayShots","HST","AST","HF","AF","HC","AC","HY","AY","HR","AR"}),
        {{"HomeTeam","Team"},{"AwayTeam","Opponent"},{"FTHG","GoalsFor"},{"FTAG","GoalsAgainst"},
         {"HTHG","HTGoalsFor"},{"HTAG","HTGoalsAgainst"},{"HS","ShotsFor"},{"AwayShots","ShotsAgainst"},
         {"HST","ShotsOnTargetFor"},{"AST","ShotsOnTargetAgainst"},{"HF","FoulsFor"},{"AF","FoulsAgainst"},
         {"HC","CornersFor"},{"AC","CornersAgainst"},{"HY","YellowFor"},{"AY","YellowAgainst"},
         {"HR","RedFor"},{"AR","RedAgainst"}}
    ),
    HomeWithVenue = Table.AddColumn(HomePerspective, "Venue", each "Home", type text),

    AwayPerspective = Table.RenameColumns(
        Table.SelectColumns(Source, {"Date","AwayTeam","HomeTeam","FTAG","FTHG","HTAG","HTHG",
            "Referee","AwayShots","HS","AST","HST","AF","HF","AC","HC","AY","HY","AR","HR"}),
        {{"AwayTeam","Team"},{"HomeTeam","Opponent"},{"FTAG","GoalsFor"},{"FTHG","GoalsAgainst"},
         {"HTAG","HTGoalsFor"},{"HTHG","HTGoalsAgainst"},{"AwayShots","ShotsFor"},{"HS","ShotsAgainst"},
         {"AST","ShotsOnTargetFor"},{"HST","ShotsOnTargetAgainst"},{"AF","FoulsFor"},{"HF","FoulsAgainst"},
         {"AC","CornersFor"},{"HC","CornersAgainst"},{"AY","YellowFor"},{"HY","YellowAgainst"},
         {"AR","RedFor"},{"HR","RedAgainst"}}
    ),
    AwayWithVenue = Table.AddColumn(AwayPerspective, "Venue", each "Away", type text),

    Combined = Table.Combine({HomeWithVenue, AwayWithVenue}),

    AddPoints = Table.AddColumn(Combined, "Points", each
        if [GoalsFor] > [GoalsAgainst] then 3 else if [GoalsFor] = [GoalsAgainst] then 1 else 0, Int64.Type),
    AddResult = Table.AddColumn(AddPoints, "Result", each
        if [GoalsFor] > [GoalsAgainst] then "W" else if [GoalsFor] = [GoalsAgainst] then "D" else "L", type text),
    AddCleanSheet = Table.AddColumn(AddResult, "CleanSheet", each
        if [GoalsAgainst] = 0 then 1 else 0, Int64.Type)
in
    AddCleanSheet
```

4. Click **Done**. You should see a 760-row table with columns `Team`, `Opponent`, `Venue`, `GoalsFor`,
   `GoalsAgainst`, `Points`, `Result`, `CleanSheet`, etc.
5. **In plain English, what this code does:** it makes two copies of every match — one relabeled from the
   home team's point of view (`Team`=home side, `GoalsFor`=their goals), one from the away team's point of
   view — then stacks the two copies into one long table, and adds three extra columns (`Points`,
   `Result`, `CleanSheet`) computed from whichever side "won" that row.
6. **Home → Close & Apply.**

You now have two tables: `season2526` (380 rows, one per match — use this for season-wide and referee
stats) and `TeamMatches` (760 rows, one per team-per-match — use this for anything grouped by team).

---

## 3. Data modeling (Model view)

Click the **Model view** icon on the left rail. You'll see two boxes (`season2526`, `TeamMatches`) with
**no line connecting them** — and that's correct, leave it that way. A relationship would need a shared
key that means "one team," but `season2526` doesn't have one (it has `HomeTeam` *and* `AwayTeam`
separately) — that mismatch is exactly why `TeamMatches` exists as its own table. Each table answers a
different set of visuals independently; nothing in this guide needs them connected.

---

## 4. DAX measures

For each measure: click the table name in the **Fields** pane → **Home → New Measure** (or right-click
the table → New Measure), then type `MeasureName = formula` exactly as shown into the formula bar and
hit Enter.

### On `season2526` (season-wide & referee stats)

| Measure | DAX | Format |
|---|---|---|
| Total Matches | `= COUNTROWS(season2526)` | Whole number |
| Total Goals | `= SUM(season2526[FTHG]) + SUM(season2526[FTAG])` | Whole number |
| Total Home Goals | `= SUM(season2526[FTHG])` | Whole number |
| Total Away Goals | `= SUM(season2526[FTAG])` | Whole number |
| Avg Goals per Match | `= DIVIDE([Total Goals], [Total Matches])` | 2 decimals |
| Avg Home Goals per Match | `= DIVIDE([Total Home Goals], [Total Matches])` | 2 decimals |
| Avg Away Goals per Match | `= DIVIDE([Total Away Goals], [Total Matches])` | 2 decimals |
| Total Yellow Cards | `= SUM(season2526[HY]) + SUM(season2526[AY])` | Whole number |
| Total Red Cards | `= SUM(season2526[HR]) + SUM(season2526[AR])` | Whole number |
| Comebacks | `= COUNTROWS(FILTER(season2526, (season2526[HTHG]<season2526[HTAG] && season2526[FTHG]>season2526[FTAG]) \|\| (season2526[HTHG]>season2526[HTAG] && season2526[FTHG]<season2526[FTAG])))` | Whole number |
| HT-FT Result Changes | `= COUNTROWS(FILTER(season2526, season2526[HTR] <> season2526[FTR]))` | Whole number |
| Matches Officiated | `= COUNTROWS(season2526)` | Whole number *(put `Referee` on rows of a table visual — see §5)* |
| Avg Fouls per Match | `= DIVIDE(SUM(season2526[HF]) + SUM(season2526[AF]), COUNTROWS(season2526))` | 1 decimal |
| Avg Cards per Match | `= DIVIDE(SUM(season2526[HY])+SUM(season2526[AY])+SUM(season2526[HR])+SUM(season2526[AR]), COUNTROWS(season2526))` | 2 decimals |

`DIVIDE(x,y)` instead of `x/y` everywhere — it's DAX's built-in "divide, but return blank instead of an
error if the bottom is zero" function. Habit worth having from day one.

### On `TeamMatches` (per-team stats)

| Measure | DAX | Format |
|---|---|---|
| Total Points | `= SUM(TeamMatches[Points])` | Whole number |
| Wins | `= CALCULATE(COUNTROWS(TeamMatches), TeamMatches[Result]="W")` | Whole number |
| Draws | `= CALCULATE(COUNTROWS(TeamMatches), TeamMatches[Result]="D")` | Whole number |
| Losses | `= CALCULATE(COUNTROWS(TeamMatches), TeamMatches[Result]="L")` | Whole number |
| Matches Played | `= COUNTROWS(TeamMatches)` | Whole number |
| Goals For | `= SUM(TeamMatches[GoalsFor])` | Whole number |
| Goals Against | `= SUM(TeamMatches[GoalsAgainst])` | Whole number |
| Goal Difference | `= [Goals For] - [Goals Against]` | Whole number |
| Shots For | `= SUM(TeamMatches[ShotsFor])` | Whole number |
| Shots On Target For | `= SUM(TeamMatches[ShotsOnTargetFor])` | Whole number |
| Conversion Rate % | `= DIVIDE([Goals For], [Shots For])` | **Percentage**, 2 decimals |
| Shot Accuracy % | `= DIVIDE([Shots On Target For], [Shots For])` | **Percentage**, 2 decimals |
| Clean Sheets | `= SUM(TeamMatches[CleanSheet])` | Whole number |
| Fouls Committed | `= SUM(TeamMatches[FoulsFor])` | Whole number |
| Yellow Cards | `= SUM(TeamMatches[YellowFor])` | Whole number |
| Red Cards | `= SUM(TeamMatches[RedFor])` | Whole number |
| Total Cards | `= [Yellow Cards] + [Red Cards]` | Whole number |
| Fouls to Card Ratio | `= DIVIDE([Fouls Committed], [Total Cards])` | 2 decimals |
| Avg Points Per Game | `= DIVIDE([Total Points], [Matches Played])` | 2 decimals |
| Home Points | `= CALCULATE([Total Points], TeamMatches[Venue]="Home")` | Whole number |
| Away Points | `= CALCULATE([Total Points], TeamMatches[Venue]="Away")` | Whole number |
| Avg Home Points | `= CALCULATE([Avg Points Per Game], TeamMatches[Venue]="Home")` | 2 decimals |
| Avg Away Points | `= CALCULATE([Avg Points Per Game], TeamMatches[Venue]="Away")` | 2 decimals |
| Home Goals For | `= CALCULATE([Goals For], TeamMatches[Venue]="Home")` | Whole number |
| Away Goals For | `= CALCULATE([Goals For], TeamMatches[Venue]="Away")` | Whole number |
| Home Clean Sheets | `= CALCULATE([Clean Sheets], TeamMatches[Venue]="Home")` | Whole number |
| Away Clean Sheets | `= CALCULATE([Clean Sheets], TeamMatches[Venue]="Away")` | Whole number |
| League Position | `= RANKX(ALL(TeamMatches[Team]), [Total Points]*1000 + [Goal Difference], , DESC, Dense)` | Whole number |

**Why `CALCULATE` keeps reappearing:** it's DAX's "recompute this measure, but under a modified filter"
function. `[Avg Home Points]` doesn't need its own new logic — it just re-runs `[Avg Points Per Game]`
with an extra filter (`Venue = "Home"`) layered on top, and both the points and the match count inside it
correctly shrink to home-only. This one pattern covers most of the "same metric, split by home/away"
measures above.

**Why `League Position` looks different:** `RANKX` needs to compare *every* team against each other,
ignoring whatever filter the visual currently has — that's what `ALL(TeamMatches[Team])` does. The
`*1000 + Goal Difference` part is a simple tiebreaker trick (points matter far more than goal difference,
so multiplying points by 1000 guarantees points always outrank GD when sorting).

---

## 5. Visualize — build these 4 pages

For each page: **Insert → New Page**, then for each visual, click its icon in the **Visualizations**
pane, then drag fields from the **Fields** pane into the wells shown (Axis / Legend / Values) at the top
of that pane.

### Page 1 — Overview

| Visual | Chart type | Fields | Why this chart |
|---|---|---|---|
| 5 KPI tiles | **Card** | one per tile: `[Total Matches]`, `[Total Goals]`, `[Avg Goals per Match]`, `[Total Yellow Cards]`, `[Total Red Cards]` | A single important number deserves a Card, not a chart — no comparison needed |
| League table | **Table** (or Matrix) | `TeamMatches[Team]`, `[League Position]`, `[Total Points]`, `[Wins]`, `[Draws]`, `[Losses]`, `[Goal Difference]`; sort by `[Total Points]` descending | 20 rows with 6+ numbers each is exactly what tables are for — a chart would be unreadable at this density |
| Points by team | **Clustered bar chart** (horizontal) | Axis: `Team`, Values: `[Total Points]`; sort descending | Horizontal bars read team names left-to-right without rotating labels — better than a column chart for 20 long category names |

### Page 2 — Team performance

| Visual | Chart type | Fields | Why this chart |
|---|---|---|---|
| Goals: home vs away | **Clustered column chart** | Axis: `Team`, Legend: `Venue`, Values: `[Goals For]` *(built on `TeamMatches`, so Venue naturally splits it)* | Clustering by a 2-value Legend (Home/Away) is the standard way to show a paired comparison per category |
| Avg points: home vs away | **Clustered column chart** | Axis: `Team`, Legend: `Venue`, Values: `[Avg Points Per Game]` | Same reasoning — direct visual comparison of the home-advantage effect, team by team |
| Clean sheets: home vs away | **Stacked bar chart** | Axis: `Team`, Legend: `Venue`, Values: `[Clean Sheets]` | Stacked (not clustered) here because the total (all clean sheets) is itself meaningful — stacking shows the whole and the split in one bar |

*Tip: Power BI sorts legend colors alphabetically by default, so "Away" gets the first color and "Home"
the second — backwards from the convention most people expect. Click each legend swatch in the Format
pane → Colors and assign them manually (teal for Home, gold for Away) rather than trusting the default
order.*

### Page 3 — Efficiency & discipline

| Visual | Chart type | Fields | Why this chart |
|---|---|---|---|
| Goal conversion rate | **Bar chart**, sorted descending | Axis: `Team`, Values: `[Conversion Rate %]` | Single metric, ranked — a sorted bar chart *is* a leaderboard |
| Shot accuracy rate | **Bar chart**, sorted descending | Axis: `Team`, Values: `[Shot Accuracy %]` | Same |
| Fouls-to-card ratio | **Bar chart**, sorted descending | Axis: `Team`, Values: `[Fouls to Card Ratio]` | Same |
| Total cards | **Bar chart**, sorted descending | Axis: `Team`, Values: `[Total Cards]` | Same |
| Referee workload | **Table** | `season2526[Referee]`, `[Matches Officiated]`, `[Avg Fouls per Match]`, `[Avg Cards per Match]` | Multiple numeric columns per referee — a table, not a chart, same reasoning as the league table |

*Avoid a pie or donut chart for any of these — with 20 teams, a donut becomes 20 slivers nobody can
compare by eye. That's a real weakness in the original 2024-25 project's dashboard, worth not repeating.*

### Page 4 — Methodology

No charts here — this page is **Text boxes** (Insert → Text box) covering: data source and citation,
the data-cleaning steps from §2, and the three statistical test results (Pearson r for clean sheets vs.
position, Pearson r for cards vs. position, paired t-test for home vs. away goals) with their p-values —
copy these from the README/HTML dashboard already in your package, since DAX has no built-in significance
testing and hand-rolling one is more risk than it's worth for a page that's meant to just state the
numbers plainly.

### Optional: a Team slicer

**Insert → Slicer**, field = `TeamMatches[Team]`. Drop it on Page 2 or 3. This is what makes the
dashboard feel "live" in front of a committee — click a team, every visual on that page filters to just
them, with no rebuilding needed. This is the single highest-value five minutes you can spend after the
core pages are built.

---

## 6. Style: fonts, colors, and the theme file

Rather than manually recoloring 15 visuals one by one, import a theme file that sets the palette once for
the whole report — every new visual then defaults to these colors automatically.

1. **View tab → Themes → Browse for themes.**
2. Select the theme file below (save it from this conversation first).
3. Done — every visual's default colors update immediately.

**What's in it, and why:**
- **Teal (`#1B4B5A`)** as the primary data color — used for Home, and as the default single-series color
- **Gold (`#B8842A`)** as the secondary color — used for Away, and any second-series comparisons
- **Green (`#3B6E52`)** reserved for "good" (used nowhere automatically, but grab it manually for
  anything meaning "positive," e.g., a Champions-League-zone indicator)
- **Red (`#A83A3A`)** reserved for "bad" (relegation zone, warnings)
- **Font: Segoe UI** throughout — it's Power BI Desktop's own native font, so it renders identically on
  any Windows machine with zero risk of a missing-font fallback during your defense

After importing the theme, two manual touches still matter:
- **Title every visual with the finding, not the field name.** "Points by team" is the field; "Arsenal's
  title-winning gap" is the finding. Double-click a visual's title text to edit it directly.
- **Sort every ranked chart descending by its value**, not alphabetically by team — click the "..." (More
  options) on the visual → Sort axis → pick the measure, not the category.

---

## 7. Before you present

- **Test every slicer and cross-filter click once, live**, not just by eyeballing the layout — rehearsed
  clicks look confident in front of a committee; fumbling for the right filter does not.
- **File → Save As**, keep a `.pbix` copy backed up somewhere outside your laptop (cloud drive/USB) in
  case of hardware issues on defense day.
- Cross-check a couple of numbers (e.g., Arsenal = 85 points, 19 clean sheets) against the README or the
  HTML dashboard from earlier — they were computed from the same underlying file, so they should match
  exactly. If anything's off, it's almost always a `Venue` filter or a `CALCULATE` typo — recheck those
  measures first.
