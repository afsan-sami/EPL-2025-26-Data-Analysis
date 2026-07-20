# ⚽ EPL 2025–26 Football Analytics

A complete football analytics project built using **MySQL, Python, and Power BI** to analyze the English Premier League 2025–26 season.

The project transforms raw match data into meaningful insights through SQL queries, statistical analysis, and interactive dashboards.

---

## 📖 Project Overview

Football generates thousands of match statistics every season. This project explores those statistics to answer questions such as:

- Which teams performed best at home and away?
- Which clubs were the most efficient in front of goal?
- How much home advantage existed throughout the season?
- Which referees issued the most cards?
- How disciplined were teams?
- Do clean sheets or disciplinary records relate to league position?

The project combines database querying, statistical testing, and data visualization into a complete analytics workflow.

---

## 🚀 Tech Stack

- **MySQL** – Data storage and SQL analysis
- **Python** – Statistical analysis
- **Pandas** – Data manipulation
- **SciPy** – Correlation & hypothesis testing
- **Power BI** – Interactive dashboard
- **Excel / CSV** – Data preparation and exports

---

## 📂 Dataset

The analysis uses the complete **Premier League 2025–26 season** dataset consisting of **380 matches**.

The dataset includes:

- Match results
- Goals
- Half-time & Full-time scores
- Shots & Shots on Target
- Fouls
- Yellow & Red Cards
- Referee information
- Home & Away statistics

---

# 🔍 Project Workflow

```
Raw Match Data
       │
       ▼
Data Cleaning
       │
       ▼
SQL Analysis (MySQL)
       │
       ▼
Statistical Analysis (Python)
       │
       ▼
Power BI Dashboard
       │
       ▼
Insights & Findings
```

---

# 📊 SQL Analysis

More than 25 SQL queries were written to analyze different aspects of the league.

### Team Performance

- League Table
- Points
- Wins / Draws / Losses
- Goal Difference
- Home vs Away Performance
- Clean Sheets

### Goal Analysis

- Total Goals
- Goal Conversion Rate
- Shot Accuracy
- Goals Scored
- Goals Conceded

### Match Analysis

- Highest Scoring Matches
- Biggest Winning Margins
- Comeback Victories
- Goal Distribution

### Discipline Analysis

- Total Fouls
- Yellow Cards
- Red Cards
- Fouls-to-Card Ratio

### Referee Analysis

- Matches Officiated
- Average Fouls per Match
- Average Cards per Match
- Card Distribution

---

# 📈 Statistical Analysis

Python was used to validate whether observed trends were statistically significant.

The notebook includes:

- League table generation
- Team statistics aggregation
- Pearson Correlation Analysis
- Paired T-Test

Statistical relationships analysed:

- Clean Sheets vs League Position
- Total Cards vs League Position
- Home Goals vs Away Goals

---

# 📊 Power BI Dashboard

The dashboard contains **5 interactive report pages**.

## 🏆 Overview

- League Champion
- Total Goals
- Home Advantage
- Comeback Matches
- Total Cards
- Interactive League Table
- Team Location Map

---

## ⚽ Team Performance

- Goals Scored (Home vs Away)
- Average Points per Game
- Home vs Away Clean Sheets

---

## 🎯 Goal Analysis

- Total Goals by Team
- Goal Conversion Rate
- Shot Accuracy

---

## 🟨 Card Analysis

- Total Fouls
- Total Cards
- Fouls-to-Card Ratio

---

## 👨‍⚖️ Referee & Discipline

- Referee Workload
- Yellow Card Distribution
- Red Card Distribution
- League Discipline Summary

---

# 💡 Key Insights

The analysis highlights:

- League-wide home advantage
- Team attacking efficiency
- Defensive consistency through clean sheets
- Shot conversion effectiveness
- Referee disciplinary patterns
- Team discipline trends
- Performance differences between home and away matches

---

# 📁 Project Structure

```
EPL-2025-26-Football-Analytics
│
├── dataset/
│   └── season-2526.csv
│
├── sql/
│   └── EPL_Queries.sql
│
├── notebook/
│   └── EPL_2025_26_Data_Analysis.ipynb
│
├── powerbi/
│   └── EPL_2025_26_Dashboard.pbix
│
├── outputs/
│   ├── csv/
│   └── excel/
│
└── README.md
```

---

# 🛠 Skills Demonstrated

- SQL
- MySQL
- Data Cleaning
- Exploratory Data Analysis (EDA)
- Statistical Analysis
- Power BI
- Dashboard Design
- Data Visualization
- Business Intelligence
- Sports Analytics

---

# 🎯 Future Improvements

Planned enhancements include:

- Expected Goals (xG)
- Possession Analysis
- Passing Accuracy
- Player-level Analytics
- Multi-League Comparison
- Automated Data Collection using APIs
- Predictive Machine Learning Models

---

# 👨‍💻 Author

**Afsan Sami**

Automation & MIS Executive | Data Analytics Enthusiast

**Skills:** SQL • Python • Power BI • Excel • Statistics

---

⭐ If you found this project useful, consider giving it a star.
