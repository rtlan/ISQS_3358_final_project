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

# Create clean player name key for future merging (this is the most important part)
df['player_name_key'] = (df['athlete_on_cover']
                         .astype(str)
                         .str.strip()
                         .str.replace(r'\s+', ' ', regex=True)
                         .str.title())

print("✅ Created 'player_name_key' column - perfect for merging with other datasets\n")

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

# 4. By Curse Verdict (Very useful for analysis!)
for verdict, group in df.groupby('curse_verdict'):
    clean_verdict = str(verdict).strip().replace(' ', '_').replace('/', '_')
    path = os.path.join(output_folder, f'04_curse_{clean_verdict}.csv')
    group.to_csv(path, index=False)
    print(f"✅ 04_curse_{clean_verdict}.csv  ({len(group)} rows)")

# 5. Bonus: Players with "Curse" vs "No Curse" for easy comparison
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
print("\nKey feature:")
print("   Every file has **player_name_key** column → easy to merge with")
print("   NFL stats, betting data, performance data, etc.")

print("\nFor your presentation:")
print("   'I took the Madden Cover Athletes Excel and split it into 5+ datasets.")
print("    I standardized player_name_key so we can easily join with external data.")
print("    This allows us to analyze the Madden Curse effect across years and teams.'")

print(f"\nRun at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
