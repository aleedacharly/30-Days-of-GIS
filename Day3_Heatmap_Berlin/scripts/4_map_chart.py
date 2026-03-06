import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Load corrected stats
df = pd.read_csv('outputs/uhi_district_stats.csv')

# Linear regression
slope, intercept, r, p, se = stats.linregress(df['ndvi_mean'], df['lst_mean'])
x_line = np.linspace(df['ndvi_mean'].min(), df['ndvi_mean'].max(), 100)
y_line = slope * x_line + intercept

print(f'Slope:     {slope:.2f}°C per NDVI unit')
print(f'Intercept: {intercept:.2f}')
print(f'R:         {r:.3f}')
print(f'p-value:   {p:.4f}')

# Plot
fig, ax = plt.subplots(figsize=(10, 7))

scatter = ax.scatter(
    df['ndvi_mean'], df['lst_mean'],
    s=150, c=df['lst_mean'],
    cmap='RdBu_r',
    vmin=df['lst_mean'].min(),
    vmax=df['lst_mean'].max(),
    edgecolors='black', linewidths=0.6, zorder=3
)

# Label each district
for _, row in df.iterrows():
    ax.annotate(
        row['name'].split('-')[0],
        (row['ndvi_mean'], row['lst_mean']),
        textcoords='offset points',
        xytext=(7, 3),
        fontsize=9
    )

# Regression line
ax.plot(x_line, y_line, color='black', linestyle='--',
        linewidth=1.5, alpha=0.7,
        label=f'Linear regression (r={r:.2f}, p={p:.3f})\nSlope: {slope:.1f}°C per NDVI unit')

plt.colorbar(scatter, ax=ax, label='Mean LST (°C)')
ax.set_xlabel('Mean NDVI (vegetation density)', fontsize=12)
ax.set_ylabel('Mean LST (°C)', fontsize=12)
ax.set_title('NDVI vs Land Surface Temperature — Berlin Districts\n'
             'Does more vegetation mean cooler surface temperatures?', fontsize=13)
ax.legend(fontsize=10, loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/ndvi_vs_lst_scatter.png', dpi=300, bbox_inches='tight')
print('Saved: outputs/ndvi_vs_lst_scatter.png')