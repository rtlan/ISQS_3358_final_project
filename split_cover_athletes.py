import pandas as pd
import os
from datetime import datetime

# ====================== CONFIGURATION ======================
excel_file = 'BI Project Cover Athletes.xlsx'   # Your exact filename
output_folder = 'cover_athletes_datasets'

os.makedirs(output_folder, exist_ok=True)

print(f"Loading your file: {excel_file}")
df = pd.read_excel(excel_file)

print(f"Total rows: {len(df)}")
print(f"Columns found: {list(df.columns)}\n")

# Basic cleaning
df.columns = [col.strip().replace(' ', '_').replace('/', '_').replace('-', '_') for col in df.columns]
df = df.dropna(how='all')  # Remove completely empty rows

# ====================== DATASET 1: All Raw Data (for reference) ======================
raw_path = os.path.join(output_folder, '01_raw_cover_athletes.csv')
df.to_csv(raw_path, index=False)
print(f"✓ Dataset 1 - Raw data saved: {raw_path} ({len(df)} rows)")

# ====================== DATASET 2: By Sport / Game Series ======================
# Splits by game (Madden, CFB, NBA2K, etc.) - very useful for comparison
if 'Game' in df.columns or 'Series' in df.columns or 'Game_Series' in df.columns:
    game_col = next((col for col in df.columns if col.lower() in ['game', 'series', 'game_series']), None)
    if game_col:
        for game, group in df.groupby(game_col):
            clean_name = str(game).replace(' ', '_').replace('/', '_')
            path = os.path.join(output_folder, f'02_{clean_name}_athletes.csv')
            group.to_csv(path, index=False)
            print(f"✓ Dataset 2 - {game}: {len(group)} rows → {path}")
else:
    print("No Game/Series column found. Skipping sport split.")

# ====================== DATASET 3: By Year / Season ======================
# Great for time-based analysis (performance before/after being cover athlete)
year_col = None
for possible in ['Year', 'Season', 'Cover_Year', 'Release_Year']:
    if possible in df.columns:
        year_col = possible
        break

if year_col:
    for year, group in df.groupby(year_col):
        path = os.path.join(output_folder, f'03_{year}_cover_athletes.csv')
        group.to_csv(path, index=False)
        print(f"✓ Dataset 3 - Year {year}: {len(group)} rows → {path}")
else:
    print("No Year column found. Using random split instead for Dataset 3.")

# ====================== DATASET 4: By Position / Conference / Division (or random if not available) ======================
position_col = None
for possible in ['Position', 'Pos', 'Role', 'Conference', 'League']:
    if possible in df.columns:
        position_col = possible
        break

if position_col:
    for value, group in df.groupby(position_col):
        clean_value = str(value).replace(' ', '_').replace('/', '_')
        path = os.path.join(output_folder, f'04_{position_col}_{clean_value}.csv')
        group.to_csv(path, index=False)
        print(f"✓ Dataset 4 - {position_col} = {value}: {len(group)} rows → {path}")
else:
    # Fallback: split into 3 roughly equal parts by rows (still useful)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    n = len(df_shuffled)
    split1 = n // 3
    split2 = 2 * split1
    
    df_shuffled.iloc[:split1].to_csv(os.path.join(output_folder, '04_part1_athletes.csv'), index=False)
    df_shuffled.iloc[split1:split2].to_csv(os.path.join(output_folder, '04_part2_athletes.csv'), index=False)
    df_shuffled.iloc[split2:].to_csv(os.path.join(output_folder, '04_part3_athletes.csv'), index=False)
    
    print(f"✓ Dataset 4 - Random split into 3 parts:")
    print(f"   Part 1: {split1} rows")
    print(f"   Part 2: {split2 - split1} rows")
    print(f"   Part 3: {n - split2} rows")

# ====================== SUMMARY ======================
print("\n" + "="*70)
print("✅ SUCCESS! All datasets created in folder: **cover_athletes_datasets**")
print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("\nRecommended structure for your GitHub:")
print("   cover_athletes_datasets/")
print("   ├── 01_raw_cover_athletes.csv")
print("   ├── 02_Madden_athletes.csv     (or similar)")
print("   ├── 03_2024_cover_athletes.csv")
print("   └── 04_QB_athletes.csv         (or part1/part2/part3)")
print("\nNext steps:")
print("1. Run this script (python split_cover_athletes.py)")
print("2. Add the folder + script to GitHub")
print("3. In your report/presentation, explain:")
print("   → You split the single Excel into 4+ domain-specific datasets")
print("   → They become much more powerful when joined (e.g. analyze performance change after being cover athlete)")
print("   → You can later join with external stats (NFL stats, betting odds, etc.)")

print("\nIf this split doesn't perfectly match your columns, reply with the list of column names from your Excel and I'll customize it instantly!")
