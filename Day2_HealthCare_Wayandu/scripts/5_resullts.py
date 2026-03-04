# scripts/05_key_results.py

import geopandas as gpd
import pandas as pd

# Load classified villages
villages = gpd.read_file('data/processed/villages_classified.geojson')

# Load PHCs
phc = gpd.read_file('data/raw/wayanad_phc_corrected.geojson')

# ── Total PHCs mapped ────────────────────────────────────────
total_phc = len(phc)

# ── Village counts per zone ──────────────────────────────────
total_villages = len(villages)

within_15 = villages[villages['access_zone'] == 'Within 15 min']
within_30 = villages[villages['access_zone'] == '15-30 min']
beyond_30 = villages[villages['access_zone'] == 'Beyond 30 min (Underserved)']

within_15_count = len(within_15)
within_30_count = len(within_30)
beyond_30_count = len(beyond_30)

within_15_pct = (within_15_count / total_villages) * 100
within_30_pct = (within_30_count / total_villages) * 100
beyond_30_pct = (beyond_30_count / total_villages) * 100

# ── Population beyond 30 min ─────────────────────────────────
pop_beyond_30 = beyond_30['population_est'].sum()

# ── Top 3 most underserved villages ─────────────────────────
top3 = beyond_30.sort_values('population_est', ascending=False).head(3)
top3_names = top3['name'].tolist()

# ── Print results ────────────────────────────────────────────
print("=" * 50)
print("        KEY RESULTS — DAY 02 WAYANAD")
print("=" * 50)
print(f"Total PHCs mapped:                {total_phc}")
print(f"Villages within 15 min:           {within_15_count} ({within_15_pct:.1f}%)")
print(f"Villages within 30 min:           {within_30_count} ({within_30_pct:.1f}%)")
print(f"Underserved villages (>30 min):   {beyond_30_count} ({beyond_30_pct:.1f}%)")
print(f"Estimated population beyond 30min:{int(pop_beyond_30):,}")
print(f"Top 3 most underserved villages:")
for i, name in enumerate(top3_names, 1):
    pop = int(top3.iloc[i-1]['population_est'])
    print(f"  {i}. {name} (population est: {pop:,})")
print("=" * 50)

# ── Also save to a text file ─────────────────────────────────
with open('outputs/key_results.txt', 'w') as f:
    f.write("KEY RESULTS — DAY 02 WAYANAD\n")
    f.write("=" * 50 + "\n")
    f.write(f"Total PHCs mapped: {total_phc}\n")
    f.write(f"Villages within 15 min: {within_15_count} ({within_15_pct:.1f}%)\n")
    f.write(f"Villages within 30 min: {within_30_count} ({within_30_pct:.1f}%)\n")
    f.write(f"Underserved villages (>30 min): {beyond_30_count} ({beyond_30_pct:.1f}%)\n")
    f.write(f"Estimated population beyond 30 min: {int(pop_beyond_30):,}\n")
    f.write(f"Top 3 most underserved villages:\n")
    for i, name in enumerate(top3_names, 1):
        pop = int(top3.iloc[i-1]['population_est'])
        f.write(f"  {i}. {name} (population est: {pop:,})\n")

print("\nResults also saved to outputs/key_results.txt")