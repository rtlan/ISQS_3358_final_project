import pandas as pd
import os
from datetime import datetime

excel_file = 'BI Project Cover Athletes.xlsx'
output_folder = 'cover_athletes_datasets'
os.makedirs(output_folder, exist_ok=True)

print(f"Loading: {excel_file}")
df = pd.read_excel(excel_file)
print(f"✅ Loaded {len(df)} rows")
print(f"Columns: {list(df.columns)}\n")

# Clean column names
df.columns = [col.strip().replace(' ', '_').replace('/', '_').lower() for col in df.columns]

# Create clean player name key for future merging
df['player_name_key'] = (df['athlete_on_cover']
                         .astype(str)
                         .str.strip()
                         .str.replace(r'\s+', ' ', regex=True)
                         .str.title())

print("✅ Created 'player_name_key' column - perfect for merging with other datasets\n")

# ====================== FIX: THREE-STATE PUSH LOGIC ======================
# The original > comparison only returns True/False, misclassifying Pushes as "No"
# This replaces it with a three-state categorical: Yes / No / Push

ou_col = 'preseason_win_total_ou'  # adjust if your column name differs
wins_col = 'cover_season_actual_wins'  # adjust if your column name differs

if ou_col in df.columns and wins_col in df.columns:
    def classify_beat_line(row):
        diff = row[wins_col] - row[ou_col]
        if diff > 0:
            return 'Yes'
        elif diff == 0:
            return 'Push'
        else:
            return 'No'

    def classify_ou_result(row):
        diff = row[wins_col] - row[ou_col]
        if diff > 0:
            return 'Over'
        elif diff == 0:
            return 'Push'
        else:
            return 'Under'

    df['beat_line'] = df.apply(classify_beat_line, axis=1)
    df['ou_result'] = df.apply(classify_ou_result, axis=1)
    df['wins_vs_line'] = df[wins_col] - df[ou_col]

    print("✅ Fixed Beat_Line → three-state (Yes / No / Push)")
    print("✅ Fixed OU_Result → three-state (Over / Under / Push)")
    print(f"   Distribution: {df['beat_line'].value_counts().to_dict()}")
    print(f"   Push seasons: {len(df[df['beat_line'] == 'Push'])}\n")
else:
    print(f"⚠️  Columns '{ou_col}' or '{wins_col}' not found — skipping Beat_Line fix")
    print(f"   Available columns: {list(df.columns)}\n")

# ====================== SAVE DATASETS ======================

# 1. Raw + Cleaned
df.to_csv(os.path.join(output_folder, '01_raw_madden_cover_athletes.csv'), index=False)
print("✅ 01_raw_madden_cover_athletes.csv  (20 rows)")

# 2. By Madden Year
for year, group in df.groupby('madden_year'):
    path = os.path.join(output_folder, f'02_madden_{int(year)}_cover_athletes.csv')
    group.to_csv(path, index=False)
    print(f"✅ 02_madden_{int(year)}_cover_athletes.csv  ({len(group)} rows)")

# 3. By Team
for team, group in df.groupby('team'):
    clean_team = str(team).strip().replace(' ', '_').replace('/', '_')
    path = os.path.join(output_folder, f'03_team_{clean_team}.csv')
    group.to_csv(path, index=False)
    print(f"✅ 03_team_{clean_team}.csv  ({len(group)} rows)")

# 4. By Curse Verdict
for verdict, group in df.groupby('curse_verdict'):
    clean_verdict = str(verdict).strip().replace(' ', '_').replace('/', '_')
    path = os.path.join(output_folder, f'04_curse_{clean_verdict}.csv')
    group.to_csv(path, index=False)
    print(f"✅ 04_curse_{clean_verdict}.csv  ({len(group)} rows)")

# 5. Curse vs No Curse comparison
curse_yes = df[df['curse_verdict'].astype(str).str.contains('curse', case=False, na=False)]
curse_no  = df[~df['curse_verdict'].astype(str).str.contains('curse', case=False, na=False)]
curse_yes.to_csv(os.path.join(output_folder, '05_curse_yes.csv'), index=False)
curse_no.to_csv(os.path.join(output_folder, '05_curse_no.csv'), index=False)
print(f"✅ 05_curse_yes.csv  ({len(curse_yes)} rows)")
print(f"✅ 05_curse_no.csv   ({len(curse_no)} rows)")

# ====================== SUMMARY ======================
print("\n" + "="*75)
print("🎉 SUCCESS! Your datasets are ready for the BI project.")
print(f"Created folder: {output_folder}")
print("\nYou now have these clean CSVs:")
print("   • 01_raw_madden_cover_athletes.csv")
print("   • Split by Madden Year")
print("   • Split by Team")
print("   • Split by Curse Verdict")
print("   • Curse_Yes vs Curse_No")
print("\nKey features:")
print("   • player_name_key → easy merge with external data")
print("   • beat_line uses three-state logic (Yes / No / Push)")
print("   • ou_result uses three-state logic (Over / Under / Push)")
print("   • wins_vs_line shows the raw differential")
print(f"\nRun at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

