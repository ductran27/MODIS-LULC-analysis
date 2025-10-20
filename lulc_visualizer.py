"""
LULC Visualizer Module
Creates visualizations for MODIS land cover analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from pathlib import Path
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class LULCVisualizer:
    """Create visualizations for land cover analysis"""
    
    # Color scheme for land cover classes (based on standard MODIS colors)
    LC_COLORS = {
        'Evergreen Needleleaf Forest': '#05450a',
        'Evergreen Broadleaf Forest': '#086a10',
        'Deciduous Needleleaf Forest': '#54a708',
        'Deciduous Broadleaf Forest': '#78d203',
        'Mixed Forests': '#009900',
        'Closed Shrublands': '#c6b044',
        'Open Shrublands': '#dcd159',
        'Woody Savannas': '#dade48',
        'Savannas': '#fbff13',
        'Grasslands': '#b6ff05',
        'Permanent Wetlands': '#27ff87',
        'Croplands': '#c24f44',
        'Urban and Built-up': '#a5a5a5',
        'Cropland/Natural Vegetation Mosaic': '#ff6d4c',
        'Snow and Ice': '#f9ffa4',
        'Barren': '#1c0dff',
        'Water Bodies': '#1919ff'
    }
    
    def __init__(self, config):
        """Initialize visualizer"""
        self.config = config
        self.plots_dir = Path('plots')
        self.plots_dir.mkdir(exist_ok=True)
        
        plt.style.use('seaborn-v0_8-whitegrid')
    
    def create_global_map(self, df, area_results, year):
        """Create global land cover map as pie chart showing area distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Pie chart showing area distribution
        class_stats = area_results['class_statistics']
        classes = list(class_stats.keys())
        percentages = [class_stats[c]['percentage'] for c in classes]
        colors = [self.LC_COLORS.get(c, '#808080') for c in classes]
        
        # Only show classes with >2% coverage
        significant = [(c, p, col) for c, p, col in zip(classes, percentages, colors) if p > 2]
        if significant:
            labels, values, colors_sig = zip(*significant)
        else:
            labels, values, colors_sig = classes[:10], percentages[:10], colors[:10]
        
        wedges, texts, autotexts = ax1.pie(values, labels=labels, colors=colors_sig,
                                            autopct='%1.1f%%', startangle=90,
                                            textprops={'fontsize': 9})
        ax1.set_title(f'Land Cover Distribution - {year}', fontsize=14, fontweight='bold')
        
        # Bar chart of top 10 classes
        top_classes = area_results['top_5_classes'][:10]
        class_names = [c['name'][:25] for c in top_classes]  # Truncate names
        class_pcts = [c['percentage'] for c in top_classes]
        bar_colors = [self.LC_COLORS.get(top_classes[i]['name'], '#808080') 
                     for i in range(len(top_classes))]
        
        ax2.barh(class_names, class_pcts, color=bar_colors, alpha=0.8, edgecolor='black')
        ax2.set_xlabel('Coverage (%)', fontsize=11)
        ax2.set_title('Top Land Cover Classes', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'global_lc_{year}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_temporal_analysis(self, area_results, change_results):
        """Create temporal trend analysis plots"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        years = sorted(area_results.keys())
        
        # Plot 1: Area trends for major classes
        major_classes = ['Croplands', 'Urban and Built-up', 
                        'Evergreen Broadleaf Forest', 'Grasslands']
        
        for lc_class in major_classes:
            areas = []
            for year in years:
                class_stats = area_results[year]['class_statistics']
                if lc_class in class_stats:
                    areas.append(class_stats[lc_class]['area_km2'])
                else:
                    areas.append(0)
            
            ax1.plot(years, areas, marker='o', linewidth=2, 
                    label=lc_class, markersize=8)
        
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Area (km²)', fontsize=12)
        ax1.set_title('Land Cover Trends Over Time', fontsize=14, fontweight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Major changes bar chart
        if len(change_results['major_changes']) > 0:
            changes = change_results['major_changes'][:10]
            classes = [c['class_name'] for c in changes]
            change_pcts = [c['change_percentage'] for c in changes]
            colors = ['green' if x > 0 else 'red' for x in change_pcts]
            
            ax2.barh(classes, change_pcts, color=colors, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Change (%)', fontsize=12)
            ax2.set_title('Major Land Cover Changes', fontsize=14, fontweight='bold')
            ax2.axvline(0, color='black', linestyle='-', linewidth=0.8)
            ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        filepath = self.plots_dir / 'temporal_analysis.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_change_map(self, all_year_data, change_results, year_start, year_end):
        """Create change comparison chart showing land cover transitions"""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Get major changes
        changes = change_results['area_changes'][:12]  # Top 12 changes
        
        class_names = [c['class_name'][:30] for c in changes]
        pixels_start = [c['pixels_start'] for c in changes]
        pixels_end = [c['pixels_end'] for c in changes]
        
        x = np.arange(len(class_names))
        width = 0.35
        
        # Create grouped bar chart
        bars1 = ax.barh(x - width/2, pixels_start, width, label=f'{year_start}',
                       color='steelblue', alpha=0.8, edgecolor='black')
        bars2 = ax.barh(x + width/2, pixels_end, width, label=f'{year_end}',
                       color='coral', alpha=0.8, edgecolor='black')
        
        ax.set_ylabel('Land Cover Class', fontsize=12)
        ax.set_xlabel('Pixel Count', fontsize=12)
        ax.set_title(f'Land Cover Change Comparison: {year_start} vs {year_end}', 
                    fontsize=16, fontweight='bold')
        ax.set_yticks(x)
        ax.set_yticklabels(class_names, fontsize=10)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add change indicators
        for i, change in enumerate(changes):
            change_pct = change['change_percentage']
            if abs(change_pct) > 2:
                color = 'green' if change_pct > 0 else 'red'
                ax.text(max(pixels_start[i], pixels_end[i]) * 1.02, i,
                       f'{change_pct:+.1f}%', va='center',
                       color=color, fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'change_comparison_{year_start}_{year_end}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
