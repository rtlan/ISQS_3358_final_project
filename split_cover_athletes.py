import pandas as pd
import os
from datetime import datetime

# ====================== CONFIGURATION ======================
excel_file = 'BI Project Cover Athletes.xlsx'
output_folder = 'cover_athletes_datasets'

os.makedirs(output_folder, exist_ok=True)

print(f"🔄 Loading: {excel_file}")

try:
    df = pd.read_excel(excel_file)
except Exception as e:
    print(f"❌ Error: {e}")
    print("   Run: pip install openpyxl")
    exit()

print(f"✅ Loaded {len(df)} rows | Columns: {list(df.columns)}\n")

# === Basic cleaning ===
df.columns = [col.strip().replace(' ', '_').replace('/', '_').replace('-', '_').lower() for col in df.columns]

# Find the player name column (common names: player, name, athlete, full_name, etc.)
player_col = None
for possible in ['player', 'player_name', 'name', 'athlete', 'full_name', 'cover_athlete']:
    if possible in df.columns:
        player_col = possible
        break

if not player_col:
    print("⚠️ Could not find a player name column. Using first column as fallback.")
    player_col = df.columns[0]

# Create a clean, standardized player name key for merging
df['player_name_key'] = (df[player_col]
                         .astype(str)
                         .str.strip()
                         .str.replace(r'\s+', ' ', regex=True)   # fix multiple spaces
                         .str.title())                           # Proper case

print(f"✅ Using '{player_col}' as player name → created 'player_name_key' for merging\n")

# ====================== DATASET 1: Raw + Cleaned ======================
raw_path = os.path.join(output_folder, '01_raw_cover_athletes.csv')
df.to_csv(raw_path, index=False)
print(f"✅ 01_raw_cover_athletes.csv  ({len(df)} rows)")

# ====================== DATASET 2: By Game / Series ======================
game_col = None
for col in ['game', 'series', 'game_series', 'title', 'sport']:
    if col in df.columns:
        game_col = col
        break

if game_col:
    for value, group in df.groupby(game_col):
        clean_name = str(value).strip().replace(' ', '_').replace('/', '_')
        path = os.path.join(output_folder, f'02_{clean_name}_athletes.csv')
        group.to_csv(path, index=False)
        print(f"✅ 02_{clean_name}_athletes.csv  ({len(group)} rows)")
else:
    print("⚠️ No Game column found → skipping split by game")

# ====================== DATASET 3: By Year ======================
year_col = None
for col in ['year', 'season', 'cover_year', 'release_year']:
    if col in df.columns:
        year_col = col
        break

if year_col:
    for value, group in df.groupby(year_col):
        path = os.path.join(output_folder, f'03_{int(value)}_cover_athletes.csv')
        group.to_csv(path, index=False)
        print(f"✅ 03_{int(value)}_cover_athletes.csv  ({len(group)} rows)")
else:
    print("⚠️ No Year column found → skipping split by year")

# ====================== DATASET 4: By Position or 3 Parts ======================
pos_col = None
for col in ['position', 'pos', 'role', 'conference', 'division']:
    if col in df.columns:
        pos_col = col
        break

if pos_col:
    for value, group in df.groupby(pos_col):
        clean_value = str(value).strip().replace(' ', '_').replace('/', '_')
        path = os.path.join(output_folder, f'04_{pos_col}_{clean_value}.csv')
        group.to_csv(path, index=False)
        print(f"✅ 04_{pos_col}_{clean_value}.csv  ({len(group)} rows)")
else:
    print("⚠️ No Position column → creating 3 equal parts instead")
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    n = len(df_shuffled)
    s1 = n // 3
    s2 = 2 * s1
    df_shuffled.iloc[:s1].to_csv(os.path.join(output_folder, '04_part1_athletes.csv'), index=False)
    df_shuffled.iloc[s1:s2].to_csv(os.path.join(output_folder, '04_part2_athletes.csv'), index=False)
    df_shuffled.iloc[s2:].to_csv(os.path.join(output_folder, '04_part3_athletes.csv'), index=False)
    print(f"✅ 04_part1_athletes.csv ({s1} rows)")
    print(f"✅ 04_part2_athletes.csv ({s2-s1} rows)")
    print(f"✅ 04_part3_athletes.csv ({n-s2} rows)")

# ====================== SUMMARY ======================
print("\n" + "="*80)
print("🎉 ALL DATASETS CREATED SUCCESSFULLY!")
print(f"Folder → {output_folder}")
print("\nImportant for your project:")
print("• Every CSV now has a column called **player_name_key**")
print("• This standardized name is perfect for merging with other datasets")
print("• You can later pull NFL/college stats, betting lines, performance data, etc.")
print("   and join everything on player_name_key")
print("\nFor your presentation say:")
print("   'We split the cover athletes Excel into multiple datasets by game, year, and position.")
print("    We also created a clean player_name_key column so all future data can be easily merged on player name.'")

print(f"\nRun date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
