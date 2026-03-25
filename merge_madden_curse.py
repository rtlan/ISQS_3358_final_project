"""
ISQS 3358 - Business Intelligence Final Project
Madden Curse Analysis: Merge Script
=====================================
This script merges 3 source datasets into a single cohesive output CSV.

Datasets:
  1. dataset1_madden_cover_athletes.csv - Cover athlete info (Source: Wikipedia/EA Sports)
  2. dataset2_player_team_performance.csv - Player & team stats (Source: Pro-Football-Reference.com)
  3. dataset3_betting_lines.csv - Preseason win total O/U lines (Source: SportsOddsHistory.com/nfelo/VegasInsider)

Merge Keys: Madden_Year + Team_Abbr
Output: merged_madden_curse_analysis.csv
"""

import pandas as pd

# ---- Load source datasets ----
ds1 = pd.read_csv('dataset1_madden_cover_athletes.csv')
ds2 = pd.read_csv('dataset2_player_team_performance.csv')
ds3 = pd.read_csv('dataset3_betting_lines.csv')

print(f"Dataset 1 (Cover Athletes):     {ds1.shape}")
print(f"Dataset 2 (Team Performance):   {ds2.shape}")
print(f"Dataset 3 (Betting Lines):      {ds3.shape}")

# ---- Data Cleaning ----
# Strip whitespace from string columns
for df in [ds1, ds2, ds3]:
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

# Verify merge keys exist and are consistent
assert set(ds1['Madden_Year']) == set(ds2['Madden_Year']) == set(ds3['Madden_Year']), \
    "Madden_Year values don't match across datasets"

# ---- Merge ----
# Step 1: Merge DS1 (athletes) with DS2 (performance) on Madden_Year + Team_Abbr
merged = pd.merge(ds1, ds2, on=['Madden_Year', 'Team_Abbr'], how='inner')
print(f"\nAfter DS1 + DS2 merge: {merged.shape}")

# Step 2: Merge with DS3 (betting lines)
merged = pd.merge(merged, ds3, on=['Madden_Year', 'Team_Abbr'], how='inner')
print(f"After DS1 + DS2 + DS3 merge: {merged.shape}")

# ---- Computed Columns (value added from merging) ----
# Win differential: cover season vs pre-cover season
merged['Win_Change'] = merged['Cover_Season_Wins'] - merged['Pre_Cover_Wins']

# Curse classification based on multiple factors
def classify_curse(row):
    """Classify curse outcome using performance + betting data together"""
    win_drop = row['Win_Change'] < 0
    missed_games = row['Games_Played_Cover_Season'] < 14
    under_line = row['OU_Result'] == 'Under'
    
    curse_signals = sum([win_drop, missed_games, under_line])
    
    if curse_signals >= 2:
        return 'Cursed'
    elif curse_signals == 0:
        return 'Broke It'
    else:
        return 'Mixed'

merged['Curse_Verdict'] = merged.apply(classify_curse, axis=1)

# Market Surprise: how far off was Vegas from reality?
merged['Market_Surprise'] = merged['Cover_Season_Actual_Wins'] - merged['Preseason_Win_Total_OU']

# Pct of games played (availability metric)
merged['Pct_Games_Played'] = (merged['Games_Played_Cover_Season'] / 16 * 100).round(1)

# ---- Select & Order Final Columns ----
final_cols = [
    'Madden_Year', 'Athlete', 'Position', 'Team', 'Team_Abbr',
    'NFL_Season', 'Salary_Avg_Per_Season',
    'Pre_Cover_Wins', 'Pre_Cover_Losses',
    'Cover_Season_Wins', 'Cover_Season_Losses', 'Win_Change',
    'Games_Played_Cover_Season', 'Pct_Games_Played',
    'Preseason_Win_Total_OU', 'Cover_Season_Actual_Wins',
    'OU_Result', 'Market_Surprise', 'Beat_Line',
    'Curse_Verdict', 'Key_Stat_Summary'
]
merged = merged[final_cols]

# ---- Save ----
merged.to_csv('merged_madden_curse_analysis.csv', index=False)
print(f"\nFinal merged dataset: {merged.shape}")
print(f"Columns: {list(merged.columns)}")

# ---- Basic Analysis ----
print("\n=== BASIC ANALYSIS ===")
print(f"\nCurse Verdict Distribution:")
print(merged['Curse_Verdict'].value_counts())

print(f"\nAverage win change (cover season vs prior): {merged['Win_Change'].mean():+.1f}")
print(f"Average market surprise (actual - line): {merged['Market_Surprise'].mean():+.2f}")
print(f"Average games played: {merged['Games_Played_Cover_Season'].mean():.1f} / 16")

print(f"\nBetting line results:")
print(merged['OU_Result'].value_counts())

print(f"\nUnder rate: {(merged['OU_Result']=='Under').sum()}/{len(merged)} = "
      f"{(merged['OU_Result']=='Under').mean()*100:.1f}%")

print("\nIf you bet UNDER on every Madden cover team's win total:")
print(f"  Record: {(merged['OU_Result']=='Under').sum()}-{(merged['OU_Result']=='Over').sum()}"
      f"-{(merged['OU_Result']=='Push').sum()} (W-L-P)")
