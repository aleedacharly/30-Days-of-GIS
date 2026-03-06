import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats


df = pd.read_csv('outputs/uhi_district_stats.csv')


fig, ax = plt.subplots(figsize=(10, 7))


# Scatter with district labels
ax.scatter(df['ndvi_mean'], df['lst_mean'], s=120, c=df['lst_mean'],
           cmap='RdBu_r', edgecolors='black', linewidths=0.5, zorder=3)
for _, row in df.iterrows():
    ax.annotate(row['name'].split('-')[0],
               (row['ndvi_mean'], row['lst_mean']),
               textcoords='offset points', xytext=(6, 3), fontsize=8)


# Regression line
slope, intercept, r, p, se = stats.linregress(df['ndvi_mean'], df['lst_mean'])
x_line = np.linspace(df['ndvi_mean'].min(), df['ndvi_mean'].max(), 100)
ax.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.6,
        label=f'Trend (r={r:.2f}, p={p:.3f})')


ax.set_xlabel('Mean NDVI (vegetation density)', fontsize=12)
ax.set_ylabel('Mean LST (°C)', fontsize=12)
ax.set_title('NDVI vs Land Surface Temperature — Berlin Districts\n(Lower vegetation = higher temperature)', fontsize=13)
ax.legend()
ax.grid(True, alpha=0.3)


plt.tight_layout()
plt.savefig('outputs/ndvi_vs_lst_scatter.png', dpi=300, bbox_inches='tight')
print(f'R = {r:.3f}, p = {p:.4f}')
